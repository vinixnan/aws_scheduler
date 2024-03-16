from optimization.generate import (
    generate_solutions,
    get_problems,
    get_pysim_data,
    generate_dict_of_performers,
)
import pytest
from dotenv import load_dotenv
from collections import namedtuple
from utils.files import get_dot, save_json
from aws.ec2 import generate_aws_dict

Config = namedtuple(
    "Config",
    "seed algorithm_name heuristic_name n_gen pop_size problem_name problem_file_path verbose eager_aws execution_id",
)

problems = [
    # "CyberShake_100.dot",
    # "Epigenomics_100.dot",
    # "Inspiral_100.dot",
    # "Montage_100.dot",
    # "Sipht_100.dot",
    # "CyberShake_1000.dot",
    "Epigenomics_24.dot",
    # "Inspiral_1000.dot",
    # "Montage_1000.dot",
    # "Sipht_1000.dot",
    "CyberShake_30.dot",
    "Epigenomics_46.dot",
    "Inspiral_30.dot",
    "Montage_25.dot",
    "Sipht_30.dot",
    "CyberShake_50.dot",
    # "Epigenomics_997.dot",
    "Inspiral_50.dot",
    "Montage_50.dot",
    "Sipht_60.dot",
]

for problem in problems:
    print("Generate", problem)
    problem = "datasets/" + problem
    problem_name = problem.split("/")[1].replace(".dot", "")
    config = Config(
        None, "NSGA2", "HEFT", 100, 100, problem_name, problem, False, False, 1
    )
    number_of_tasks = int(get_dot(config.problem_file_path) / 2)
    dccv, regions = generate_aws_dict(["US East (N. Virginia)"], config.eager_aws)
    problems = get_problems(number_of_tasks, regions, dccv, config.problem_file_path)
    all_perfomance = {}
    for p in problems:
        all_perfomance[p.region] = generate_dict_of_performers(p, dccv)
    save_json(all_perfomance, "performance_data/" + problem_name + ".json")
