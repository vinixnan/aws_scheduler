import pytest
from dotenv import load_dotenv
from optimization.experiment import run_experiment
from utils.definitions import Config

load_dotenv()

algs = [
    "NSGA",
    "AGEMOEA",
    #"SMSEMOA",
]


def generate_solutions(
    alg,
    heu,
    pop=5,
    gen=2,
):
    problem = "CyberShake_30.dot"
    problem_file_path = "datasets/" + problem
    problem_name = problem_file_path.split("/")[1].replace(".dot", "")
    config = Config(
        7,
        alg,
        heu,
        gen,
        pop,
        problem_name,
        problem,
        False,
        False,
        666,
        "us-east-1",
    )
    n_threads = 1
    arr = run_experiment(config, problem_file_path, n_threads)
    assert len(arr["population"]) > 0


def test_HEFT():
    for alg in algs:
        generate_solutions(alg, "HEFT")


def test_PEFT():
    for alg in algs:
        generate_solutions(alg, "PEFT")


def test_HSIP():
    for alg in algs:
        generate_solutions(alg, "HSIP", 10)

def test_MPEFT():
    for alg in algs:
        generate_solutions(alg, "MPEFT", 10)
