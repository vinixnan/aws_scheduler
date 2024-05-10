import random

import click
from dotenv import load_dotenv
from optimization.experiment import run_experiment
from utils.definitions import Config

load_dotenv()

algs = [
    "HEFT",
    "PEFT",
    "HSIP",
    "MPEFT",
]


@click.command()
@click.option("--idexec", help="Id execution", required=True, default=666)
@click.option(
    "--problem",
    "-p",
    help="Path for the problem definition (.dot file)",
    required=True,
    default="Montage_100.dot",
)
@click.option(
    "--alg",
    "-a",
    help="Algorithm in (NSGA2, AGEMOEA, SMSEMOA, MOEAD)",
    default="NSGA2",
)
@click.option("--heu", "-h", help="Heuristic in " + str(algs), default="PEFT")
@click.option("--pop", help="Pop size ", default=50)
@click.option("--gen", help="Generation", default=250)
def run(
    idexec,
    problem,
    alg,
    heu,
    pop,
    gen,
):
    problem_file_path = "datasets/" + problem
    problem_name = problem_file_path.split("/")[1].replace(".dot", "")
    config = Config(
        random.randint(0, 10000),
        alg,
        heu,
        gen,
        pop,
        problem_name,
        problem,
        False,
        False,
        idexec,
        "us-east-1",
    )
    n_threads = 5
    run_experiment(config, problem_file_path, n_threads)


if __name__ == "__main__":
    run()
