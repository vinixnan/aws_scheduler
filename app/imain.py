from aws.ec2 import get_aws_regions_full
from optimization.generate import (
    generate_solutions,
    select_one_solution,
)

from dotenv import load_dotenv
import numpy as np
from collections import namedtuple
from utils.files import save_yaml, format_solution
import click

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
    "seed algorithm_name heuristic_name n_gen pop_size problem_name problem_file_path verbose eager_aws execution_id interative",
)


def run_exp(config):
    full_name_regions = get_aws_regions_full()
    print("Generating solutions for " + str(full_name_regions))
    non_dominated_population = generate_solutions(config, full_name_regions)
    # non_dominated_population has as objective price per hour and power
    s, filtered = select_one_solution(non_dominated_population)

    # print(format_solution(s))

    to_save = dict(config._asdict())
    to_save["population"] = [format_solution(ss) for ss in filtered]
    to_save["selected"] = format_solution(s)
    to_save["selections"] = {}

    file_output = (
        "output/"
        + config.algorithm_name
        + "_"
        + str(config.execution_id)
        + "_"
        + config.problem_name
        + "_"
        + config.heuristic_name
        + ".yml"
    )
    save_yaml(to_save, file_output)


@click.command()
@click.option("--idexec", help="Id execution", required=True)
@click.option(
    "--problem",
    "-p",
    help="Path for the problem definition (.dot file)",
    required=True,
)
@click.option(
    "--alg",
    "-a",
    help="Algorithm in " + str(algs),
    default=["NSGA2", "AGEMOEA", "SMSEMOA"],
)
@click.option("--heu", "-h", help="Heuristic in " + str(algs))
@click.option("--pop", help="Pop size ", default=100)
@click.option("--gen", help="Generation", default=500)
def run(
    idexec,
    problem,
    alg,
    heu,
    pop,
    gen,
):
    problem = "datasets/" + problem
    problem_name = problem.split("/")[1].replace(".dot", "")
    config = Config(
        None, alg, heu, gen, pop, problem_name, problem, False, False, idexec, True
    )
    run_exp(config)


if __name__ == "__main__":
    run()
