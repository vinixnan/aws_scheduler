from collections import defaultdict, OrderedDict, deque
from optimization.heuristic.base import (
    recursive_transverse,
    calc_EST,
    generate_L,
    generate_C,
    generate_W,
    generate_B,
    generate_W_line,
    OCT,
)
import math
from pysim_helper import Machine


def generate_rank_d(
    B_m_n,
    B_m_n_line,
    w_line,
    machines,
    task_names,
    machine_types,
    dataset_machines,
    w,
    succ,
    data,
):
    L_m, L_line = generate_L(len(machines))
    c_proc_i_j, c_i_j_line = generate_C(task_names, machines, succ, L_line, data, B_m_n, B_m_n_line)

    succ = OrderedDict(sorted(succ.items(), key=lambda x: len(x[1])))
    rank_d = {}
    for task in succ.keys():
        recursive_transverse(task, succ, c_i_j_line, w_line, rank_d)

    rank_d = OrderedDict(sorted(rank_d.items(), key=lambda x: x[1], reverse=True))
    return rank_d, c_proc_i_j


def generate_assignment(machines, w, pred, c_proc_i_j, rank_d):
    assignment = defaultdict(list)
    assigned_task = {}
    for task_id in rank_d.keys():
        machines_est = {}
        for machine_name, machine_data in machines.items():
            dt = calc_EST(task_id, machine_name, assignment, pred, c_proc_i_j, assigned_task)
            data = {}
            data["EST"] = dt["AFT"]
            data["AFT"] = data["EST"] + w[machine_data.data["name"]][task_id]
            data["machine"] = machine_name
            data["name"] = task_id
            machines_est[machine_name] = data

        machines_est = OrderedDict(sorted(machines_est.items(), key=lambda x: x[1]["AFT"]))
        selected = list(machines_est.keys())[0]
        selected_data = machines_est[selected]

        selected_machine_type = machines[selected].data
        selected_data["machine_type"] = selected_machine_type

        assigned_task[task_id] = selected_data
        assignment[selected].append(selected_data)

    last_host = None
    first_host = None
    makespan = 0
    for host_name, l in assignment.items():
        data = l[-1]
        if data["AFT"] > makespan:
            makespan = data["AFT"]
            last_host = host_name
        data = l[0]
        if data["EST"] == 0:
            first_host = host_name

    return assignment, makespan, first_host, last_host
