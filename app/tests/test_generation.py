from optimization.generate import (
    generate_solutions,
    get_problems,
    get_pysim_data,
    generate_dict_of_performers,
)
import pytest
from dotenv import load_dotenv
from collections import namedtuple
from utils.files import get_dot
from aws.ec2 import generate_aws_dict

load_dotenv()


def test_generate_solutions():
    Config = namedtuple(
        "Config",
        "seed algorithm_name heuristic_name n_gen pop_size problem_name problem_file_path verbose eager_aws execution_id",
    )
    problem = "basic_graph.dot"
    problem = "datasets/" + problem
    problem_name = problem.split("/")[1].replace(".dot", "")
    config = Config(
        None, "NSGA2", "HEFT", 3, 100, problem_name, problem, False, False, 1
    )
    arr = generate_solutions(config, ["US East (N. Virginia)"])
    assert len(arr) > 50
    resp = get_pysim_data(arr[0], ["HEFT"], {})
    assert resp != None


def test_generate_dict():
    Config = namedtuple(
        "Config",
        "seed algorithm_name heuristic_name n_gen pop_size problem_name problem_file_path verbose eager_aws execution_id",
    )
    problem = "basic_graph.dot"
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
    print(all_perfomance)
