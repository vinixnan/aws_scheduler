from aws.ec2 import get_aws_regions_full
from optimization.generate import (
    generate_solutions,
    get_pysim_data,
    select_one_solution,
)
from optimization.problem import invert_maximization, remove_dominated
from dotenv import load_dotenv
import numpy as np
from collections import namedtuple
from utils.files import save_yaml, format_solution

load_dotenv()

algs = [
    "DLS",
    "HCPT",
    "HEFT",
    "Lookahead",
    "PEFT",
    # "SimHEFT",
]

Config = namedtuple(
    "Config",
    "seed algorithm_name n_gen pop_size problem_file_path verbose eager_aws execution_id",
)

config = Config(1, "SMSEMOA", 100, 50, "datasets/Montage_25.dot", False, False, 1)


full_name_regions = get_aws_regions_full()
# full_name_regions = [full_name_regions[0]]
print("Generating solutions for " + str(full_name_regions))
non_dominated_population = generate_solutions(config, full_name_regions)
non_dominated_population_n = []
print(len(non_dominated_population))
print("Running scheduler")
selections = {}
for sol in non_dominated_population:
    get_pysim_data(sol, algs, selections)
    non_dominated_population_n.append(sol)

non_dominated_population = non_dominated_population_n
print("Removing non-dominated")

non_dominated_population = remove_dominated(non_dominated_population)


s, filtered = select_one_solution(non_dominated_population)
invert_maximization(filtered)

print(format_solution(s))

to_save = dict(config._asdict())
to_save["population"] = [format_solution(ss) for ss in filtered]
to_save["selected"] = format_solution(s)
to_save["selections"] = selections

save_yaml(to_save, config.algorithm_name + "_" + str(config.execution_id) + ".yml")
