from aws.ec2 import generate_aws_dict
from utils.files import get_dot
from optimization.algorithm import run_all
from optimization.problem import remove_dominated, get_problems
from utils.files import save_xml, save_json
from optimization.problem import Instance
import subprocess
import tempfile
import json
import numpy as np
from collections import defaultdict, OrderedDict


class Solution:
    def __init__(self, problem):
        self.problem = problem
        self.F = [0, 0]
        self.X = []


def generate_dict_of_performers(problem, dccv):
    performance = defaultdict(dict)
    for machine in dccv[problem.region]:
        sol = Solution(problem)
        sol.x_aws = [machine] * 2
        get_pysim_data(sol, ["HEFT"], {})
        dcx = sol.x_aws_tasks
        for machine_name in list(dcx.keys()):
            to_add = {dc["name"]: (dc["finish_time"] - dc["start_time"]) for dc in dcx[machine_name]}
            performance[machine_name].update(to_add)

    return performance


def generate_solutions(config, full_name_regions):
    print(config)
    number_of_tasks = int(get_dot(config.problem_file_path) / 5)
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
            s.fitness = s.fitness + ((s.F[i] - min_data[i]) / (max_data[i] - min_data[i]))
            s.valid = True
            if s.F[i] > mean_data[i]:
                s.valid = False
        s.fitness = float(s.fitness)

    filtered = list(filter(lambda s: s.valid, population))
    return min(filtered, key=lambda s: s.fitness), filtered


def get_simple_decision(x_aws_tasks):
    task_in_host = OrderedDict()
    for k, values in x_aws_tasks.items():
        for v in values:
            task_in_host[v["name"]] = k
    return task_in_host


def generate_instances(sol, problem):
    # add the smallest machine if necessary
    if len(sol.x_aws) < 2:
        sol.x_aws.insert(0, problem.smaller_machine["name"])
    machines = {}
    for id_instance, instance_type in enumerate(sol.x_aws):
        ins = Instance(id_instance, instance_type, problem.base[instance_type])
        machines[ins.name] = ins

    sol.machines = machines


def update_used_instances(sol, tasks):
    for ins in sol.machines.values():
        if tasks.get(ins.name) and len(tasks.get(ins.name)) > 0:
            ins.active = True
            ins.tasks = tasks.get(ins.name)
        else:
            ins.active = False
            ins.tasks = []

    sol.x_aws = [machine.instance_type for machine in sol.machines.values()]
    sol.x_aws_tasks = tasks


def calc_makespan(solution):
    task_in_host = get_simple_decision(solution.x_aws_tasks)
    tf_json = tempfile.NamedTemporaryFile()
    save_json(task_in_host, tf_json.name)
    problem = solution.problem
    tf_xml = tempfile.NamedTemporaryFile()

    xml_data = problem.generate_simgrid_xml(solution.machines)
    save_xml(xml_data, tf_xml.name)
    p = subprocess.Popen(
        "runsimulation --hostconf " + tf_xml.name + " -p " + problem.problem_file_path + " -a " + tf_json.name,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    retval = p.wait()
    if retval == 0:
        returned_str = p.stdout.readlines()[0].decode("utf-8").rstrip()
        data = json.loads(returned_str)
        print(data)
    else:
        print(xml_data)
        print(p.stdout.readlines())


def get_pysim_data(solution, algs, selections):
    problem = solution.problem
    generate_instances(solution, problem)
    tf = tempfile.NamedTemporaryFile()
    xml_data = problem.generate_simgrid_xml(solution.machines)
    save_xml(xml_data, tf.name)
    data_arr = []
    for alg in algs:
        p = subprocess.Popen(
            "pysim --conf " + tf.name + " -p " + problem.problem_file_path + " -a " + alg,
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
    update_used_instances(solution, selected["tasks"])
    solution.alg = selected["alg"]
    problem.update_decision_variables(solution, makespan)
    return makespan
