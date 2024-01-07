from aws.ec2 import get_aws_regions_full
from optimization.generate import (
    generate_solutions,
    get_pysim_data,
    select_one_solution,
)
from optimization.problem import invert_maximization, remove_dominated
from dotenv import load_dotenv
import numpy as np

load_dotenv()

algs = [
    "DLS",
    "HCPT",
    "HEFT",
    "Lookahead",
    "PEFT",
    # "SimHEFT",
]

dot_file = "datasets/Montage_25.dot"
dot_file = "datasets/Montage_1000.dot"
full_name_regions = get_aws_regions_full()
full_name_regions = [full_name_regions[0]]
print("Generating solutions for " + str(full_name_regions))
non_dominated_population = generate_solutions(dot_file, full_name_regions, 1, False)
non_dominated_population_n = []
print(len(non_dominated_population))
print("Running scheduler")
for sol in non_dominated_population:
    get_pysim_data(sol, algs)
    non_dominated_population_n.append(sol)

non_dominated_population = non_dominated_population_n
print("Removing non-dominated")
print(len(non_dominated_population))
non_dominated_population = remove_dominated(non_dominated_population)
print(len(non_dominated_population))


print(len(non_dominated_population))

s = select_one_solution(non_dominated_population)
print(s.x_aws, s.F, s.region, s.x_aws_tasks, s.valid, s.fitness)
invert_maximization(non_dominated_population)
print(s.x_aws, s.F, s.region, s.x_aws_tasks, s.valid, s.fitness)
