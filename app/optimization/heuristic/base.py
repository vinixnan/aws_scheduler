from collections import defaultdict, OrderedDict
from pysim_helper import Machine
from pysim_helper import get_pysim_data
import os
from utils.files import save_yaml, read_yaml


def recursive_transverse(task, succ, c_i_j_line, w_line, memo):
    if memo.get(task):
        return memo[task]

    if not succ[task]:
        memo[task] = w_line[task]
        return memo[task]

    to_see = []
    for suc in succ[task]:
        val = (
            recursive_transverse(suc, succ, c_i_j_line, w_line, memo)
            + c_i_j_line[task][suc]
        )
        to_see.append(val)

    memo[task] = max(to_see) + w_line[task]
    return memo[task]


def calc_EST(task, task_machine, assignment, pred, c_proc_i_j, memo):
    if memo.get(task):
        return memo[task]

    values = []
    for t in pred.get(task, []):
        data = calc_EST(t, task_machine, assignment, pred, c_proc_i_j, memo)
        cj = c_proc_i_j[t][task][data["machine"]][task_machine]
        val = data["AFT"] + cj
        values.append(val)

    to_return = 0
    if values:
        to_return = max(values)

    data = {}
    data["AFT"] = to_return
    machine_assignment = assignment[task_machine]
    if machine_assignment:
        if machine_assignment[-1]["AFT"] > to_return:
            data = machine_assignment[-1]

    return data


def generate_B(dataset_machines, machine_types, machines):
    all_networks = [
        (dataset_machines[machine_type]["networkPerformance"])
        for machine_type in machine_types
    ]
    B_m_n_line = sum(all_networks) / len(all_networks)
    B_m_n = {
        machine_name: (machine_data.data["networkPerformance"])
        for machine_name, machine_data in machines.items()
    }
    return B_m_n, B_m_n_line


def generate_L(qtd_machine):
    L_m = 0.00000001 * 1000
    L_line = [0.00000001 * 1000] * qtd_machine
    L_m = 0
    L_line = [0] * qtd_machine
    return L_m, L_line


def generate_C(task_names, machines, succ, L_line, data, B_m_n, B_m_n_line):
    c_proc_i_j = {}

    for task_i in task_names:
        for machine_type_i in machines.keys():
            for task_j in task_names:
                if task_i != task_j:
                    for machine_type_j in machines.keys():
                        task_i_dependent = succ.get(task_i, [])
                        if task_j in task_i_dependent:
                            value = 0
                            if machine_type_j != machine_type_i:
                                value = (sum(L_line) / len(L_line)) + (
                                    data[task_i][task_j] / B_m_n[machine_type_j]
                                )

                            if not c_proc_i_j.get(task_i):
                                c_proc_i_j[task_i] = {}
                            if not c_proc_i_j[task_i].get(task_j):
                                c_proc_i_j[task_i][task_j] = {}
                            if not c_proc_i_j[task_i][task_j].get(machine_type_i):
                                c_proc_i_j[task_i][task_j][machine_type_i] = {}

                            c_proc_i_j[task_i][task_j][machine_type_i][
                                machine_type_j
                            ] = value

    c_i_j_line = defaultdict(dict)
    for task_i in task_names:
        for task_j in task_names:
            if task_i != task_j:
                task_i_dependent = succ.get(task_i, [])
                if task_j in task_i_dependent:
                    c_i_j_line[task_i][task_j] = (sum(L_line) / len(L_line)) + (
                        data[task_i][task_j] / B_m_n_line
                    )

    return c_proc_i_j, c_i_j_line


def generate_W_line(w, task_names, machine_types):
    w_line = defaultdict(dict)
    for task in task_names:
        all_task_size = [w[machine_type][task] for machine_type in machine_types]
        w_line[task] = sum(all_task_size) / len(all_task_size)
    return w_line


def generate_W(
    task_names,
    config,
    problem,
    problem_file_path,
    region,
    regions,
    region_machines_dataset,
    machine_types,
):
    all_processors_weights = load_processors_weights(
        config, problem, problem_file_path, regions, region_machines_dataset
    )
    w = all_processors_weights[region]

    return w, generate_W_line(w, task_names, machine_types)


def load_processors_weights(
    config, problem, problem_file_path, regions, region_machines_dataset
):
    eager = config.eager_aws
    eager = True
    if eager or not os.path.isfile(problem + "_machine_execution_time.yml"):
        dc_region_machines_task_time = {}
        for region in regions:
            dataset_machines = region_machines_dataset[region]
            dc_machines_task_time = {}
            for machine_name, machine_data in dataset_machines.items():
                selected_region_machines = [machine_data] * 2
                machines = {}
                for i, machine_data in enumerate(selected_region_machines):
                    mach = Machine("host" + str(i), machine_data, "link" + str(i))
                    machines[mach.name] = mach

                resp = get_pysim_data(machines, problem_file_path, "HEFT", False)
                tasks = {}
                for host_tasks in resp["tasks"].values():
                    for task in host_tasks:
                        tasks[task["name"]] = task["finish_time"] - task["start_time"]

                dc_machines_task_time[machine_name] = {}
                dc_machines_task_time[machine_name] = tasks

            dc_region_machines_task_time[region] = dc_machines_task_time

        save_yaml(dc_region_machines_task_time, problem + "_machine_execution_time.yml")

    else:
        dc_region_machines_task_time = read_yaml(
            problem + "_machine_execution_time.yml"
        )

    return dc_region_machines_task_time
