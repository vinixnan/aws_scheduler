from optimization.generate import generate_solutions, get_pysim_data
import pytest
from dotenv import load_dotenv
from collections import namedtuple

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
        None, "NSGA2", "HEFT", 100, 100, problem_name, problem, False, False, 1
    )
    arr = generate_solutions(config, ["US East (N. Virginia)"])
    assert len(arr) > 50
    resp = get_pysim_data(arr[0], ["HEFT"], {})
    assert resp != None
