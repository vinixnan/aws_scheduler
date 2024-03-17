from aws.ec2 import get_aws_regions_full, generate_aws_dict
from utils.files import get_dot
import math
from collections import Counter
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
from pysim_helper import get_pysim_data
import numpy as np

from dotenv import load_dotenv

load_dotenv()


problem_file_path = "datasets/CyberShake_100.dot"
n_threads = 3
pop_size = 50
gen = 100

# Get data
full_name_regions = get_aws_regions_full()
number_of_tasks = int(get_dot(problem_file_path))
region_machines_dataset, regions = generate_aws_dict(full_name_regions, False)

# remove dominated per region
print("Before remove dominated regions", len(region_machines_dataset.keys()))
region_machines_dataset = remove_non_dominated_per_region(region_machines_dataset)
print("After remove dominated regions", len(region_machines_dataset.keys()))
region_machines_dataset, n_var, ndom_base = remove_bad_performing_machines(
    region_machines_dataset, number_of_tasks, problem_file_path
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
        )
        problems[region_name] = problem

# run GA for all problems and add everyone to the same pop
pop = []
for region_name, machines_data in region_machines_dataset.items():
    if len(machines_data) > 1:
        problem = problems[region_name]
        print(problem.region_name)
        alg = Algorithm("NSGAII", gen, pop_size, problem, problem.region_name)

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

        resp = get_pysim_data(machines, problem_file_path, "HEFT")
        machines = {k: v for k, v in machines.items() if k in resp["tasks"].keys()}
        sol.makespan = resp["makespan"]
        sol.tasks = resp["tasks"]
        sol.X = [
            v.data["name"] for k, v in machines.items() if k in resp["tasks"].keys()
        ]
        sol.price = math.ceil(float(resp["makespan"]) / 3600) * sum(
            [machine.data["pricePerUnit"] for machine in machines.values()]
        )
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


# print results
for sol in npop:
    problem = problems[sol.region_name]
    element = (
        (sol.F[0], sol.F[1]),
        (sol.X, sol.region_name, sol.tasks),
    )
    objs, data = element
    if objs[0] <= avg_makespan and objs[1] < avg_price:
        print(Counter(data[0]), data[1], objs)
