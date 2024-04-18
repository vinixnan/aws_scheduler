from collections import namedtuple

import click
import numpy as np
from aws.ec2 import get_aws_regions_full
from dotenv import load_dotenv
from optimization.generate import calc_makespan, generate_solutions, get_pysim_data, select_one_solution
from optimization.problem import remove_dominated
from utils.files import format_solution, save_json, save_yaml

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
    "seed algorithm_name heuristic_name n_gen pop_size problem_name problem_file_path verbose eager_aws execution_id",
)


def run_exp(config):
    full_name_regions = get_aws_regions_full()
    print("Generating solutions for " + str(full_name_regions))
    full_name_regions = "US East (N. Virginia)"
    non_dominated_population = generate_solutions(config, full_name_regions)
    # non_dominated_population has as objective price per hour and power
    print(len(non_dominated_population), "non-dominated solutions")
    print("Running scheduler")
    selections = {}
    for sol in non_dominated_population:
        get_pysim_data(sol, [config.heuristic_name], selections)

    # not each solution in non_dominated_population have as objective the price and the makespan
    print("Removing non-dominated from the new problem setup")
    non_dominated_population = remove_dominated(non_dominated_population)

    s, filtered = select_one_solution(non_dominated_population)
    calc_makespan(s)
    # print(format_solution(s))
    print(len(non_dominated_population), "non-dominated solutions")

    to_save = dict(config._asdict())
    to_save["population"] = [format_solution(ss) for ss in filtered]
    to_save["selected"] = format_solution(s)
    to_save["selections"] = selections

    file_output = (
        "output/"
        + config.algorithm_name
        + "_"
        + str(config.execution_id)
        + "_"
        + config.problem_name
        + "_"
        + config.heuristic_name
    )
    # save_yaml(to_save, file_output + ".yml")
    save_json(to_save, file_output + ".json")


@click.command()
@click.option("--idexec", help="Id execution", required=True, default=0)
@click.option(
    "--problem",
    "-p",
    help="Path for the problem definition (.dot file)",
    required=True,
    default="CyberShake_100.dot",
)
@click.option(
    "--alg",
    "-a",
    help="Algorithm in (NSGA2, AGEMOEA, SMSEMOA)",
    default="NSGA2",
)
@click.option("--heu", "-h", help="Heuristic in " + str(algs), default="HEFT")
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
    config = Config(None, alg, heu, gen, pop, problem_name, problem, False, False, idexec)
    run_exp(config)


if __name__ == "__main__":
    run()
