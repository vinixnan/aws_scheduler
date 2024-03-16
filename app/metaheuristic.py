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
from collections import defaultdict, Counter
from aws_preprocessing import remove_non_dominated_per_region
from optimization.algorithm import Algorithm
from optimization.generate import get_simple_decision
import numpy as np
from pymoo.core.problem import ElementwiseProblem
import time

load_dotenv()


Machine = namedtuple("Machine", "name data link")


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
                    latency="0.00000001s",
                )
            keys = list(machines.keys())
            routes = defaultdict(dict)
            for i in range(len(keys)):
                origin = machines[keys[i]]
                for j in range(len(keys)):
                    if i != j and routes[i].get(j) is None:
                        routes[i][j] = True
                        routes[j][i] = True
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


problem_file_path = "datasets/CyberShake_100.dot"

# Get data
full_name_regions = get_aws_regions_full()
number_of_tasks = int(get_dot(problem_file_path))
dccv, regions = generate_aws_dict(full_name_regions, False)

# remove dominated per region

final_region_machines = remove_non_dominated_per_region(dccv)
n_var = int(number_of_tasks / 3)

def calc_makespan(machines, x_aws_tasks, problem_file_path):
    task_in_host = get_simple_decision(x_aws_tasks)
    tf_json = tempfile.NamedTemporaryFile()
    save_json(task_in_host, tf_json.name)
    tf_xml = tempfile.NamedTemporaryFile()

    xml_data = generate_simgrid_xml(machines)
    save_xml(xml_data, tf_xml.name)
    p = subprocess.Popen(
        "runsimulation --hostconf "
        + tf_xml.name
        + " -p "
        + problem_file_path
        + " -a "
        + tf_json.name,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    retval = p.wait()
    if retval == 0:
        returned_str = p.stdout.readlines()[0].decode("utf-8").rstrip()
        data = json.loads(returned_str)
        return data
    else:
        print(xml_data)
        print(p.stdout.readlines())

class AWSProblemDirect(ElementwiseProblem):
    def __init__(self, n_var, machines_data, region_name, problem_file_path, elementwise_runner=None):
        self.region_name = region_name
        self.machines_data = machines_data
        self.problem_file_path = problem_file_path
        self.ids = {k: v for k, v in enumerate(self.machines_data.keys(), 1)}
        self.ids_rev = {v: k for k, v in self.ids.items()}
        print(region_name, self.ids)
        xl = np.zeros(n_var)
        xu = np.ones(n_var) * max(self.ids.keys())
        print(n_var)
        self.ccc = 0
        
        self.memo = defaultdict()
        super().__init__(n_var=n_var, n_obj=2, n_constr=1, xl=xl, xu=xu, vtype=int, elementwise_runner=elementwise_runner)

    def pysim(self, selected_region_machines):
        machines = {}
        for i, machine_data in enumerate(selected_region_machines):
            mach = Machine("host" + str(i), machine_data, "link" + str(i))
            machines[mach.name] = mach

        resp = get_pysim_data(machines, problem_file_path, "HEFT")
        machines = {k: v for k, v in machines.items() if k in resp["tasks"].keys()}
        price = math.ceil(float(resp["makespan"]) / 3600) * sum(
            [machine.data["pricePerUnit"] for machine in machines.values()]
        )
        return resp["makespan"], price, resp["tasks"]

    def _evaluate(self, x, out, *args, **kwargs):
        makespan, price, tasks, violations = self.calculate_fitness(x)
        out["F"] = [makespan, price]
        out["G"] = [violations]

    def show_solution(self, sol):
        return [self.ids[x] for x in sol.X if x > 0]

    def calculate_fitness(self, X):
        used_machines = [self.machines_data[self.ids[ins]] for ins in X if ins > 0]
        violations = 0
        if len(used_machines) <= 1:
            violations = len(used_machines)
            return float("inf"), float("inf"), None, violations
        
        
        k = tuple(sorted([ins for ins in X if ins > 0]))
        if self.memo.get(k):
            data = self.memo[k]
        else:
            makespan, price, tasks = self.pysim(used_machines)
            data={}
            data['makespan']=makespan
            data['price']=price
            data['tasks']=tasks
            self.memo[k] = data
        
        self.ccc = self.ccc + 1
        return data['makespan'], data['price'], data['tasks'], 0

class AWSProblem(ElementwiseProblem):
    def __init__(self, n_var, machines_data, region_name):
        self.region_name = region_name
        self.machines_data = machines_data
        self.ids = {k: v for k, v in enumerate(self.machines_data.keys(), 1)}
        self.ids_rev = {v: k for k, v in self.ids.items()}
        print(region_name, self.ids)
        xl = np.zeros(n_var)
        xu = np.ones(n_var) * max(self.ids.keys())
        print(n_var)
        super().__init__(n_var=n_var, n_obj=2, n_constr=1, xl=xl, xu=xu, vtype=int)

    def _evaluate(self, x, out, *args, **kwargs):
        ecu, price_per_ecu, network_performance, violations = self.calculate_fitness(x)
        out["F"] = [ecu, network_performance]
        out["G"] = [violations]

    def show_solution(self, sol):
        return [self.ids[x] for x in sol.X if x > 0]

    def calculate_fitness(self, X):
        used_machines = [self.machines_data[self.ids[ins]] for ins in X if ins > 0]
        violations = 0
        if len(used_machines) == 0:
            violations = 2
        elif len(used_machines) == 1:
            violations = 1

        network_performance = sum([v["pricePerUnit"] for v in used_machines])
        price_per_ecu = sum([v["price_per_ecu"] for v in used_machines])
        ecu = sum([v["ecu"] for v in used_machines]) * -1
        return ecu, price_per_ecu, network_performance, violations

from multiprocessing.pool import ThreadPool
from pymoo.core.problem import StarmapParallelization
n_threads = 6
pool = ThreadPool(n_threads)
runners = StarmapParallelization(pool.starmap)

# create problems for all region considering non dominated machines
memo = defaultdict()
problems = {}
for region_name, machines_data in final_region_machines.items():
    problem = AWSProblemDirect(n_var + 1, machines_data, region_name, problem_file_path, elementwise_runner=runners)
    problem.memo=memo
    problems[region_name] = problem




prob = problems["us-east-1"]
problems = {}
problems["us-east-1"] = prob

# run GA for all problems and add everyone to the same pop
pop = []
pop_size = 30
gen = 100
avg_makespan = avg_price = 20

for problem in problems.values():
    for i in range(5):
        problem = AWSProblemDirect(n_var + 1, machines_data, region_name, problem_file_path, elementwise_runner=runners)
        problem.memo = memo
        print(problem.region_name)
        #algorithm_name, n_gen, pop_size, problem, region, seed=None, verbose=False
        alg = Algorithm("NSGAII", gen, pop_size, problem, problem.region_name)
        
        start_time = time.time()
        res = alg.run()
        print("--- %s seconds ---" % (time.time() - start_time))
        print(problem.ccc, len(problem.memo))
            
        for sol in res.pop:
            sol.region_name = problem.region_name
        pop.extend(res.pop)


def dominates_sol(s1s, s2s):
    s1 = s1s.F
    s2 = s2s.F
    better = 0
    eq = 0
    worse = 0
    for i in range(len(s1)):
        if s1[i] < s2[i]:
            better = better + 1
        elif s1[i] == s2[i]:
            eq = eq + 1
        else:
            worse = worse + 1

    if better == len(s1):
        # fullly dominates
        return 1
    if worse == len(s1):
        # fully dominated
        return -1
    if eq == len(s1):
        # exactly the same
        return 0

    if better > 0 and worse == 0:
        # dominates a little
        return 1
    if worse > 0 and better == 0:
        # is dominated a little
        return -1
    return 0


def remove_dominated_sol(pop):
    returning = []
    for i in range(len(pop)):
        dominated = False
        for j in range(len(pop)):
            if i != j:
                if dominates_sol(pop[i], pop[j]) == -1:
                    dominated = True
                    break
        if not dominated:
            returning.append(pop[i])
    return returning


# remove dominates and repeated
print("len pop", len(pop))
npop = remove_dominated_sol(pop)
print("len npop", len(npop))

print("remove repeated")
dc = {}
for sol in npop:
    k = (sum(sol.X), tuple(sol.F), sol.region_name)
    dc[k] = sol
npop = list(dc.values())
print("len npop", len(npop))


# run everyone in pysim, update solutions

for sol in npop:
    region_machines = final_region_machines[sol.region_name]
    problem = problems[sol.region_name]
    selected_region_machines = [
        region_machines[machine_name] for machine_name in problem.show_solution(sol)
    ]

    machines = {}
    for i, machine_data in enumerate(selected_region_machines):
        mach = Machine("host" + str(i), machine_data, "link" + str(i))
        machines[mach.name] = mach

    resp = get_pysim_data(machines, problem_file_path, "HEFT")
    machines = {k: v for k, v in machines.items() if k in resp["tasks"].keys()}
    sol.makespan = resp["makespan"]
    sol.tasks = resp["tasks"]
    sol.price = math.ceil(float(resp["makespan"]) / 3600) * sum(
        [machine.data["pricePerUnit"] for machine in machines.values()]
    )
    sol.oldF = sol.F
    sol.F = np.array([sol.makespan, sol.price])

# remove dominated considering makespan and cost
print("len pop", len(npop))
npop = remove_dominated_sol(npop)
print("len npop", len(npop))

all_makespan = []
all_price = []
for sol in npop:
    all_makespan.append(sol.F[0])
    all_price.append(sol.F[1])


#avg_makespan = sum(all_makespan) / len(all_makespan)
#avg_price = sum(all_price) / len(all_price)


# print results
for sol in npop:
    problem = problems[sol.region_name]
    if sol.F[0] <= avg_makespan and sol.F[1] < avg_price:
        print(Counter(problem.show_solution(sol)), sol.F, sol.region_name)
