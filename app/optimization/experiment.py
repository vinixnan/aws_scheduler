import math
import os
import time

from aws.aws_preprocessing import remove_bad_performing_machines, remove_non_dominated_per_region
from aws.ec2 import generate_aws_dict, generate_data_transfer_dict, get_aws_regions_full
from dask.distributed import Client, LocalCluster
from dotenv import load_dotenv
from optimization.algorithm import Algorithm
from optimization.heuristic.base import generate_W
from optimization.heuristic.heft import HEFT
from optimization.heuristic.hsip import HSIP
from optimization.heuristic.peft import PEFT
from optimization.problem import AWSProblemDirect, remove_dominated_sol
from pymoo.config import Config
from pymoo.core.problem import DaskParallelization
from utils.definitions import Machine
from utils.files import format_solution, get_dot, get_total_input, load_xml_data, read_json, save_json

Config.warnings["not_compiled"] = False

very_start_time = time.time()

load_dotenv()


def get_heuristic(heuristic_name, w, machines_data, succ, pred, data):
    if heuristic_name == "HEFT":
        return HEFT(w, machines_data, succ, pred, data)
    if heuristic_name == "PEFT":
        return PEFT(w, machines_data, succ, pred, data)
    if heuristic_name == "HSIP":
        return HSIP(w, machines_data, succ, pred, data)


def data_generation(config, problem_file_path):
    # Get data
    print("data gen", config)
    size_of_dataset_in_gb = get_total_input(problem_file_path.replace(".dot", ".xml")) / 1024 / 1024 / 1024
    full_name_regions = get_aws_regions_full()
    number_of_tasks = int(get_dot(problem_file_path)) - 2
    print("dataset size", size_of_dataset_in_gb / number_of_tasks * 1024, number_of_tasks)
    region_machines_dataset, regions = generate_aws_dict(full_name_regions, config.eager_aws)
    data_trasfer_cost = generate_data_transfer_dict(config.eager_aws)
    from_origin_data_trasfer_cost = data_trasfer_cost[config.starting_region]
    from_origin_data_trasfer_cost = {k: v * size_of_dataset_in_gb for k, v in from_origin_data_trasfer_cost.items()}
    # print(from_origin_data_trasfer_cost)
    generate_W(config, config.problem_name, problem_file_path, regions, region_machines_dataset)
    # remove dominated per region
    print("Before remove dominated regions", len(region_machines_dataset.keys()))
    region_machines_dataset = remove_non_dominated_per_region(region_machines_dataset)
    print("After remove dominated regions", len(region_machines_dataset.keys()))
    region_machines_dataset, n_var, _ = remove_bad_performing_machines(
        region_machines_dataset,
        number_of_tasks,
        from_origin_data_trasfer_cost,
        problem_file_path,
    )
    print(
        "After remove dominated machines in execution",
        len(region_machines_dataset),
        region_machines_dataset.keys(),
    )
    print("Number of tasks", number_of_tasks, "Average of number of executed machines", n_var)
    save_json(region_machines_dataset, "ndmachines/" + config.problem_name + "_nd_regions.json")


def run_experiment(config, problem_file_path, n_threads):
    # Get data
    machine_nd_name = "ndmachines/" + config.problem_name + "_nd_regions.json"
    if not os.path.isfile(machine_nd_name):
        data_generation(config, problem_file_path)
    else:
        print("read it")
        region_machines_dataset = read_json(machine_nd_name)

    problem_xml_name = problem_file_path.replace(".dot", ".xml")
    data, graph, pred, succ = load_xml_data(problem_xml_name, problem_file_path)
    regions = list(region_machines_dataset.keys())
    n_var = int(len(graph) * 0.05 + 3)

    W = generate_W(config, config.problem_name, problem_file_path, regions, region_machines_dataset)

    problems = {}
    full_name_regions = get_aws_regions_full()
    region_machines_dataset, regions = generate_aws_dict(full_name_regions, config.eager_aws)
    # region_machines_dataset = {
    #    region_name: machines_data for region_name, machines_data in region_machines_dataset.items() if machines_data
    # }
    qtd_valid_regions = len(region_machines_dataset)
    gen = int(math.ceil(config.n_gen / qtd_valid_regions))
    print(config, "valid_regions=" + str(qtd_valid_regions), "gen=" + str(gen), "n_var=" + str(n_var))
    pop = []
    cluster = LocalCluster(n_workers=n_threads)
    client = Client(cluster)
    print("DASK STARTED")
    for region_name, machines_data in region_machines_dataset.items():
        if len(machines_data) > 1:
            w = W[region_name]
            heu = get_heuristic(config.heuristic_name, w, machines_data, succ, pred, data)
            client.restart()
            runners = DaskParallelization(client)
            problem = AWSProblemDirect(
                n_var,
                machines_data,
                region_name,
                problem_file_path,
                elementwise_runner=runners,
                heu=heu,
            )
            problems[region_name] = problem
            print(problem.region_name)

            alg = Algorithm(config.algorithm_name, gen, config.pop_size, problem, problem.region_name)

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

    to_save = dict(config._asdict())
    to_save["population"] = [format_solution(ss, problems) for ss in npop]
    to_save["n_var"] = n_var
    to_save["considered_regions"] = list(region_machines_dataset.keys())

    file_output = (
        "outputx/"
        + config.algorithm_name
        + "_"
        + str(config.execution_id)
        + "_"
        + config.problem_name
        + "_"
        + config.heuristic_name
    )
    save_json(to_save, file_output + ".json")
    print("Finished --- %s seconds ---" % (time.time() - very_start_time))
    return to_save
