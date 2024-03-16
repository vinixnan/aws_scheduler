from aws.ec2 import get_aws_regions_full, generate_aws_dict
from utils.files import get_dot
from pymoo.util.ref_dirs import get_reference_directions
from utils.files import save_xml, save_json
import tempfile
import subprocess
from yattag import Doc, indent
import json
from dotenv import load_dotenv
from collections import namedtuple
import math
from pyomo.environ import *

load_dotenv()


def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


def generate_simgrid_xml(machines):
    doc, tag, _ = Doc().tagtext()
    doc.asis("<?xml version='1.0'?>")
    doc.asis(
        '<!DOCTYPE platform SYSTEM "http://simgrid.gforge.inria.fr/simgrid/simgrid.dtd">'
    )

    with tag("platform", version="4"):
        with tag("AS", id="AS0", routing="Floyd"):
            for machine in machines.values():
                doc.stag(
                    "host",
                    id=machine.name,
                    core=machine.data["vcpu"],
                    speed=machine.data["flop"],
                )
                doc.stag(
                    "link",
                    id=machine.link,
                    bandwidth=str(machine.data["networkPerformance"]) + "Bps",
                    latency="0.0001s",
                )
            keys = list(machines.keys())
            origin = machines[keys[0]]
            for j in range(1, len(keys)):
                destiny = machines[keys[j]]
                with tag("route", src=origin.name, dst=destiny.name):
                    doc.stag("link_ctn", id=origin.link)

    return indent(doc.getvalue(), indentation=" " * 4, newline="\r\n")


def get_pysim_data(combination, problem_file_path, alg):
    tf = tempfile.NamedTemporaryFile()
    xml_data = generate_simgrid_xml(combination)
    save_xml(xml_data, tf.name)
    p = subprocess.Popen(
        "pysim --conf " + tf.name + " -p " + problem_file_path + " -a " + alg,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    retval = p.wait()
    if retval == 0:
        returned_str = p.stdout.readlines()[0].decode("utf-8").rstrip()
        data = json.loads(returned_str)
        data["alg"] = alg
    else:
        print(xml_data)
        print(p.stdout.readlines())

    return data


problem_file_path = "datasets/CyberShake_30.dot"

full_name_regions = get_aws_regions_full()
number_of_tasks = int(get_dot(problem_file_path))
dccv, regions = generate_aws_dict(full_name_regions, False)

all_machines = []
for region_data in dccv.values():
    for data in region_data.values():
        all_machines.append(data)

max_ecu = max([machine["ecu"] for machine in all_machines])
min_ecu = min([machine["ecu"] for machine in all_machines])
max_price = max([machine["pricePerUnit"] for machine in all_machines])
min_price = min([machine["pricePerUnit"] for machine in all_machines])

max_vcpu = max([machine["vcpu"] for machine in all_machines])
min_vcpu = min([machine["vcpu"] for machine in all_machines])

max_memory = max([machine["memory"] for machine in all_machines])
min_memory = min([machine["memory"] for machine in all_machines])

max_price_per_ecu = max([machine["price_per_ecu"] for machine in all_machines])
min_price_per_ecu = min([machine["price_per_ecu"] for machine in all_machines])


for region_data in dccv.values():
    for data in region_data.values():
        data["n_ecu"] = normalize(data["ecu"], min_ecu, max_ecu)
        data["n_pricePerUnit"] = normalize(data["pricePerUnit"], min_price, max_price)
        data["n_vcpu"] = normalize(data["vcpu"], min_vcpu, max_vcpu)
        data["n_memory"] = normalize(data["memory"], min_memory, max_memory)
        data["n_price_per_ecu"] = normalize(
            data["price_per_ecu"], min_price_per_ecu, max_price_per_ecu
        )


n_partitions = 10
weights_set = get_reference_directions(
    "das-dennis", 2, n_partitions=n_partitions, scaling=1
)
print(len(weights_set))

selected_data = {}
for region_name, dccv_nd in dccv.items():
    chosen = []
    for weights in weights_set:
        bestval = float("inf")
        best_machine = None
        for machine_name, data in dccv_nd.items():
            val = (1 - data["n_ecu"]) * weights[0] + data["n_pricePerUnit"] * weights[1]
            if val < bestval:
                bestval = val
                best_machine = machine_name
        chosen.append(best_machine)
    chosen = set(chosen)
    selected_data[region_name] = {
        k: v for k, v in dccv[region_name].items() if k in chosen
    }

print(selected_data["us-east-1"])

Machine = namedtuple("Machine", "name data link")

final_mach = {}
for machine_name, data in dccv["us-east-1"].items():
    machines = {}
    # number_of_tasks = 2
    for i in range(number_of_tasks):
        mach = Machine("host" + str(i), data, "link" + str(i))
        machines[mach.name] = mach

    resp = get_pysim_data(machines, problem_file_path, "HEFT")
    machines = {k: v for k, v in machines.items() if k in resp["tasks"].keys()}

    name = list(machines.keys())[0]

    machine = machines[name].data

    machine["makespan"] = resp["makespan"]
    machine["price"] = (
        machine["pricePerUnit"]
        * len(machines)
        * (math.ceil(float(resp["makespan"]) / 3600))
    )
    print(len(machines), machine["name"], machine["makespan"], machine["price"])
    final_mach[machine["name"]] = machine

max_price = max([machine["price"] for machine in final_mach.values()])
min_price = min([machine["price"] for machine in final_mach.values()])
max_makespan = max([machine["makespan"] for machine in final_mach.values()])
min_makespan = min([machine["makespan"] for machine in final_mach.values()])
# print(final_mach)
for machine in final_mach.values():
    machine["n_price"] = normalize(data["price"], min_price, max_price)
    machine["n_makespan"] = normalize(data["makespan"], min_makespan, max_makespan)


def generate_permutations_lp(data, max_size, weights, max_repeated_machine, max_money):
    model = ConcreteModel()

    # Define the set of elements
    items = list(data.keys())
    model.E = Set(initialize=items)

    # Define the range of combination sizes
    model.R = RangeSet(0, max_size)

    # Binary decision variables to indicate inclusion of elements in combinations
    # model.x = Var(model.E, model.R, within=NonNegativeReals, bounds=(0, max_size))
    model.x = Var(model.E, model.R, domain=Binary)

    model.obj = Objective(
        expr=sum(
            data[e]["n_makespan"] * model.x[e, r] * weights[0]
            + data[e]["n_price"] * model.x[e, r] * weights[1]
            for e in model.E
            for r in model.R
        ),
        sense=minimize,
    )

    model.one_combination_per_machine = Constraint(
        model.R, rule=lambda model, r: sum(model.x[e, r] for e in model.E) == 1
    )

    # model.other = Constraint(model.E, rule=lambda model, e: sum(model.x[e, r] for r in model.R) <= max_repeated_machine)

    model.money_contraint = Constraint(
        rule=sum(
            model.x[e, r] * data[e]["n_pricePerUnit"] for e in model.E for r in model.R
        )
        <= max_money
    )

    # Solve the LP
    solver = SolverFactory("glpk")
    solver.options["tmlim"] = 3
    results = solver.solve(model)

    # Extract the solution
    pre_solution = [[e] * int(model.x[e, r].value) for e in model.E for r in model.R]
    solution = []
    for s in pre_solution:
        solution.extend(s)

    return solution


# from collections import Counter
# for weights in weights_set:
#    finale=generate_permutations_lp(final_mach, 10, weights, 10, 20)
#   cnt = Counter(finale)
#   va=sum([final_mach[k]['price'] * qtd for k,qtd in cnt.items()])
#   makespans=[final_mach[k]['makespan'] for k,qtd in cnt.items()]
#   print(cnt, weights, va, makespans)


for weights in weights_set:
    bestval = float("inf")
    best_machine = None
    best_data = None
    for machine_name, data in final_mach.items():
        val = (data["n_price"]) * weights[0] + data["n_makespan"] * weights[1]
        if val < bestval:
            bestval = val
            best_machine = machine_name
            best_data = data
    print(weights, best_machine, bestval, best_data)
