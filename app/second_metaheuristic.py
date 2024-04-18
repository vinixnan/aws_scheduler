from aws.ec2 import get_aws_regions_full, generate_aws_dict, generate_data_transfer_dict
from utils.files import get_dot, get_total_input
import math
from collections import namedtuple
from pysim_helper import Machine
from aws_preprocessing import (
    remove_non_dominated_per_region,
    remove_dominated,
    remove_bad_performing_machines,
)
from optimization.algorithm import Algorithm
import time
from multiprocessing.pool import ThreadPool
from pymoo.core.problem import StarmapParallelization
from mop_helper import AWSProblemDirect, remove_dominated_sol
from pysim_helper import get_pysim_data, calc_makespan
import numpy as np
from utils.files import format_solution_b, save_json
import sys
import os
from utils.files import save_yaml, read_yaml, load_xml_data, get_dot_full

from optimization.heuristic.heft import (
    generate_rank_d,
    generate_assignment,
    el_test,
)
from collections import defaultdict, OrderedDict
import tempfile
from utils.files import save_xml, save_json
from optimization.heuristic.base import generate_W, generate_B

from dotenv import load_dotenv

very_start_time = time.time()

load_dotenv()

Config = namedtuple(
    "Config",
    "seed algorithm_name heuristic_name n_gen pop_size problem_name problem_file_path verbose eager_aws execution_id starting_region",
)


args = sys.argv[1:]
print(args)

problem = "Cybershake_100.dot"
# problem = "Cybershake_30.dot"
# problem = "Epigenomics_24.dot"
alg = "NSGAII"
alg = "AGEMOEA"
heu = "HEFT"
idexec = 666
pop_size = 50
gen = 2

if args:
    problem = args[0]
    alg = args[1]
    heu = args[2]
    idexec = int(args[3])
    pop_size = int(args[4])
    gen = int(args[5])

print(problem, alg, heu, idexec, pop_size, gen)

problem_file_path = "datasets/" + problem
n_threads = 5


problem_name = problem_file_path.split("/")[1].replace(".dot", "")

problem_xml_name = problem_file_path.replace(".dot", ".xml")

el_test()

config = Config(
    None,
    alg,
    heu,
    gen,
    pop_size,
    problem_name,
    problem,
    False,
    False,
    idexec,
    "us-east-1",
)
# Get data
# size_of_dataset_in_gb=get_total_input(problem_file_path.replace(".dot", ".xml")) / 1024 / 1024 / 1024
full_name_regions = get_aws_regions_full()
number_of_tasks = int(get_dot(problem_file_path)) - 2
# print("dataset size",size_of_dataset_in_gb/number_of_tasks * 1024, number_of_tasks)
region_machines_dataset, regions = generate_aws_dict(
    full_name_regions, config.eager_aws
)


region_machines_dataset = {"us-east-1": region_machines_dataset["us-east-1"]}
region_machines_dataset["us-east-1"] = {
    "m1.small": region_machines_dataset["us-east-1"]["m1.small"]
}
region_machines_dataset["us-east-1"]["m1.small"]["networkPerformance"] = 1000000000
regions = ["us-east-1"]

eager = config.eager_aws


data, graph, pred, succ = load_xml_data(problem_xml_name, problem_file_path)
task_names = list(graph.keys())
datax = data


for region in regions:
    dataset_machines = region_machines_dataset[region]

    # create test array with machine name

    qtd_machine = 2
    machine_types = []
    machines_names = list(dataset_machines.keys())
    machine_types = [machines_names[0]] * qtd_machine

    w, w_line = generate_W(
        task_names,
        config,
        problem,
        problem_file_path,
        region,
        regions,
        region_machines_dataset,
        machine_types,
    )

    machines = {}
    for i, machine_data in enumerate(machine_types):
        mach = Machine("host" + str(i), dataset_machines[machine_data], "link" + str(i))
        machines[mach.name] = mach
    # create test array with machine name
    B_m_n, B_m_n_line = generate_B(dataset_machines, machine_types, machines)

    rank_d, c_proc_i_j = generate_rank_d(
        B_m_n,
        B_m_n_line,
        w_line,
        machines,
        task_names,
        machine_types,
        dataset_machines,
        w,
        succ,
        data,
    )
    assignment, makespan, first_host, last_host = generate_assignment(
        machines, w, pred, c_proc_i_j, rank_d
    )
    assignment[last_host].append(
        {
            "machine": last_host,
            "name": "end",
            "AFT": assignment[last_host][-1],
            "EST": assignment[last_host][-1],
        }
    )
    assignment[first_host].insert(
        0, {"machine": last_host, "name": "root", "AFT": 0, "EST": 0}
    )
    resp2 = calc_makespan(machines, assignment, problem_file_path)
    print(makespan, resp2["makespan"])
    import pdb

    pdb.set_trace()


data_trasfer_cost = generate_data_transfer_dict(config.eager_aws)
from_origin_data_trasfer_cost = data_trasfer_cost[config.starting_region]
from_origin_data_trasfer_cost = {
    k: v * size_of_dataset_in_gb for k, v in from_origin_data_trasfer_cost.items()
}
# print(from_origin_data_trasfer_cost)


# remove dominated per region
print("Before remove dominated regions", len(region_machines_dataset.keys()))
region_machines_dataset = remove_non_dominated_per_region(region_machines_dataset)
print("After remove dominated regions", len(region_machines_dataset.keys()))
region_machines_dataset, n_var, ndom_base = remove_bad_performing_machines(
    region_machines_dataset,
    number_of_tasks,
    from_origin_data_trasfer_cost,
    problem_file_path,
)
print(
    "After remove dominated machines in execution",
    len(region_machines_dataset),
    region_machines_dataset.keys(),
)
print(
    "Number of tasks", number_of_tasks, "Average of number of executed machines", n_var
)
pool = ThreadPool(n_threads)
runners = StarmapParallelization(pool.starmap)

problems = {}
for region_name, machines_data in region_machines_dataset.items():
    if len(machines_data) > 1:
        problem = AWSProblemDirect(
            n_var + 1,
            machines_data,
            region_name,
            problem_file_path,
            elementwise_runner=runners,
            heu=config.heuristic_name,
        )
        problems[region_name] = problem

# run GA for all problems and add everyone to the same pop
pop = []
for region_name, machines_data in region_machines_dataset.items():
    if len(machines_data) > 1:
        problem = problems[region_name]
        print(problem.region_name)
        alg = Algorithm(
            config.algorithm_name, gen, pop_size, problem, problem.region_name
        )

        start_time = time.time()
        res = alg.run()
        print("--- %s seconds ---" % (time.time() - start_time))

        for sol in res.pop:
            sol.region_name = problem.region_name
        pop.extend(res.pop)

# remove dominates and repeated
print("MOEA generated population", len(pop))
npop = remove_dominated_sol(pop)
print("MOEA generated non-dominated population", len(npop))

dc = {}
for sol in npop:
    k = (sum(sol.X), tuple(sol.F), sol.region_name)
    dc[k] = sol
npop = list(dc.values())
print("MOEA generated after removing repeated", len(npop))


# run everyone in pysim, update solutions
print("Run to get taks")
for sol in npop:
    region_machines = region_machines_dataset[sol.region_name]
    if len(region_machines) > 1:
        problem = problems[sol.region_name]
        selected_region_machines = [
            region_machines[machine_name] for machine_name in problem.show_solution(sol)
        ]

        machines = {}
        for i, machine_data in enumerate(selected_region_machines):
            mach = Machine("host" + str(i), machine_data, "link" + str(i))
            machines[mach.name] = mach

        resp = get_pysim_data(machines, problem_file_path, config.heuristic_name)
        machines = {k: v for k, v in machines.items() if k in resp["tasks"].keys()}
        sol.makespan = resp["makespan"]
        sol.tasks = resp["tasks"]
        sol.X = [
            v.data["name"] for k, v in machines.items() if k in resp["tasks"].keys()
        ]
        sol.price = math.ceil(float(resp["makespan"]) / 3600) * sum(
            [machine.data["pricePerUnit"] for machine in machines.values()]
        ) + from_origin_data_trasfer_cost.get(region_name, 0)
        sol.oldF = sol.F
        sol.F = np.array([sol.makespan, sol.price])

# remove dominated considering makespan and cost
npop = remove_dominated_sol(npop)
print("MOEA generated non-dominated population", len(npop))

all_makespan = []
all_price = []
for sol in npop:
    all_makespan.append(sol.F[0])
    all_price.append(sol.F[1])
    element = (
        (sol.F[0], sol.F[1]),
        (sol.X, sol.region_name, sol.tasks),
    )
    ndom_base.append(element)


avg_makespan = sum(all_makespan) / len(all_makespan)
avg_price = sum(all_price) / len(all_price)


ndom_base = remove_dominated(ndom_base)
print("Final size of population", len(ndom_base))
print("avg_makespan", avg_makespan, "avg_price", avg_price)


to_save = dict(config._asdict())
to_save["population"] = [format_solution_b(ss) for ss in npop]
to_save["avg_makespan"] = avg_makespan
to_save["avg_price"] = avg_price
to_save["n_var"] = n_var
to_save["considered_regions"] = list(region_machines_dataset.keys())

file_output = (
    "outputf/"
    + config.algorithm_name
    + "_"
    + str(config.execution_id)
    + "_"
    + config.problem_name
    + "_"
    + config.heuristic_name
)
save_json(to_save, file_output + ".json")
print("Finished --- %s seconds ---" % (time.time() - very_start_time))
