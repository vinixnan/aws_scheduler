from aws.ec2 import generate_aws_dict
from utils.files import get_dot
from optimization.algorithm import run_all
from optimization.problem import remove_dominated, get_problems
from utils.files import save_xml
import subprocess
import tempfile
import json
import numpy as np


def generate_solutions(config, full_name_regions):
    print(config)
    number_of_tasks = int(get_dot(config.problem_file_path) / 2)
    dccv, regions = generate_aws_dict(full_name_regions, config.eager_aws)
    problems = get_problems(number_of_tasks, regions, dccv, config.problem_file_path)
    all_regions_pop = run_all(problems, config)
    non_dominated_population = remove_dominated(all_regions_pop)
    return non_dominated_population


def select_one_solution(population):
    qtd_obj = 2
    max_data = []
    min_data = []
    mean_data = []
    for i in range(qtd_obj):
        all_fitness = [s.F[i] for s in population]
        el_max = max(all_fitness)
        el_min = min(all_fitness)
        el_mean = sum(all_fitness) / len(population)
        max_data.append(el_max)
        min_data.append(el_min)
        mean_data.append(el_mean)
    for s in population:
        s.fitness = 0
        for i in range(qtd_obj):
            s.fitness = s.fitness + (
                (s.F[i] - min_data[i]) / (max_data[i] - min_data[i])
            )
            s.valid = True
            if s.F[i] > mean_data[i]:
                s.valid = False
        s.fitness = float(s.fitness)

    filtered = list(filter(lambda s: s.valid, population))
    return min(filtered, key=lambda s: s.fitness), filtered


def get_pysim_data(solution, algs, selections):
    problem = solution.problem
    tf = tempfile.NamedTemporaryFile()
    xml_data, machines = problem.generate_simgrid_xml(solution)
    save_xml(xml_data, tf.name)
    data_arr = []
    for alg in algs:
        p = subprocess.Popen(
            "pysim --conf "
            + tf.name
            + " -p "
            + problem.problem_file_path
            + " -a "
            + alg,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        retval = p.wait()
        if retval == 0:
            returned_str = p.stdout.readlines()[0].decode("utf-8").rstrip()
            data = json.loads(returned_str)
            data["alg"] = alg
            data_arr.append(data)
        else:
            print(xml_data)
            print(p.stdout.readlines())
    selected = min(data_arr, key=lambda x: x["makespan"])

    selections[selected["alg"]] = 1 + selections.get(selected["alg"], 0)

    makespan = float(selected["makespan"])
    tasks = selected["tasks"]
    ids = [int(el.replace("host", "")) for el in tasks.keys()]
    solution.x_aws = [machines[id][0] for id in ids]
    solution.x_aws_tasks = {machines[int(k.replace("host", ""))][0]:v for k,v in tasks.items()}
    solution.alg = selected["alg"]
    problem.update_decision_variables(solution, makespan)
    return makespan
