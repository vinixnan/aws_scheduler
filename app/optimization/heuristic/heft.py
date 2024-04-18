from collections import defaultdict, OrderedDict
from optimization.heuristic.base import (
    recursive_transverse,
    calc_EST,
    generate_L,
    generate_C,
    generate_W,
    generate_B,
    generate_W_line,
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
    c_proc_i_j, c_i_j_line = generate_C(
        task_names, machines, succ, L_line, data, B_m_n, B_m_n_line
    )

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
            dt = calc_EST(
                task_id, machine_name, assignment, pred, c_proc_i_j, assigned_task
            )
            data = {}
            data["EST"] = dt["AFT"]
            data["AFT"] = data["EST"] + w[machine_data.data["name"]][task_id]
            data["machine"] = machine_name
            data["name"] = task_id
            machines_est[machine_name] = data

        machines_est = OrderedDict(
            sorted(machines_est.items(), key=lambda x: x[1]["AFT"])
        )
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


def generate_data_heft_paper():
    task_names = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"]
    machines = {"P1": {}, "P2": {}, "P3": {}}
    for m in machines.keys():
        machines[m] = Machine(m, {"name": m}, "link" + m)

    machine_types = list(machines.keys())
    w = defaultdict(dict)
    rank_u_test = {}

    w["P1"]["T1"] = 14
    w["P1"]["T2"] = 13
    w["P1"]["T3"] = 11
    w["P1"]["T4"] = 13
    w["P1"]["T5"] = 12
    w["P1"]["T6"] = 13
    w["P1"]["T7"] = 7
    w["P1"]["T8"] = 5
    w["P1"]["T9"] = 18
    w["P1"]["T10"] = 21

    w["P2"]["T1"] = 16
    w["P2"]["T2"] = 19
    w["P2"]["T3"] = 13
    w["P2"]["T4"] = 8
    w["P2"]["T5"] = 13
    w["P2"]["T6"] = 16
    w["P2"]["T7"] = 15
    w["P2"]["T8"] = 11
    w["P2"]["T9"] = 12
    w["P2"]["T10"] = 7

    w["P3"]["T1"] = 9
    w["P3"]["T2"] = 18
    w["P3"]["T3"] = 19
    w["P3"]["T4"] = 17
    w["P3"]["T5"] = 10
    w["P3"]["T6"] = 9
    w["P3"]["T7"] = 11
    w["P3"]["T8"] = 14
    w["P3"]["T9"] = 20
    w["P3"]["T10"] = 16

    succ = {}
    succ["T1"] = ["T2", "T3", "T4", "T5", "T6"]
    succ["T2"] = ["T8", "T9"]
    succ["T3"] = ["T7"]
    succ["T4"] = ["T8", "T9"]
    succ["T5"] = ["T9"]
    succ["T6"] = ["T8"]

    succ["T7"] = ["T10"]
    succ["T8"] = ["T10"]
    succ["T9"] = ["T10"]
    succ["T10"] = []

    data = defaultdict(dict)
    data["T1"]["T2"] = 18
    data["T1"]["T3"] = 12
    data["T1"]["T4"] = 9
    data["T1"]["T5"] = 11
    data["T1"]["T6"] = 14

    data["T2"]["T8"] = 19
    data["T2"]["T9"] = 16

    data["T3"]["T7"] = 23
    data["T4"]["T8"] = 27
    data["T4"]["T9"] = 23
    data["T5"]["T9"] = 13
    data["T6"]["T8"] = 15

    data["T7"]["T10"] = 17
    data["T8"]["T10"] = 11
    data["T9"]["T10"] = 13

    rank_u_test["T1"] = 108
    rank_u_test["T2"] = 77
    rank_u_test["T3"] = 80
    rank_u_test["T4"] = 80
    rank_u_test["T5"] = 69
    rank_u_test["T6"] = 63.333
    rank_u_test["T7"] = 42.667
    rank_u_test["T8"] = 35.667
    rank_u_test["T9"] = 44.333
    rank_u_test["T10"] = 14.667

    return task_names, machines, machine_types, w, data, rank_u_test, succ


def el_test():
    (
        task_names,
        machines,
        machine_types,
        w,
        data,
        rank_u_test,
        succ,
    ) = generate_data_heft_paper()
    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    rank_d, c_proc_i_j = generate_rank_d(
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
    )

    for task in task_names:
        # print(task, rank_d[task], rank_u_test[task])
        assert math.isclose(rank_d[task], rank_u_test[task], rel_tol=0.01)


def el_test2():
    task_names = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"]
    machines = {"P1": {}, "P2": {}, "P3": {}}
    machine_types = list(machines.keys())
    w = defaultdict(dict)
    rank_u_test = {}

    w["P1"]["T1"] = 64
    w["P1"]["T2"] = 42
    w["P1"]["T3"] = 27
    w["P1"]["T4"] = 42
    w["P1"]["T5"] = 28
    w["P1"]["T6"] = 42
    w["P1"]["T7"] = 13
    w["P1"]["T8"] = 13
    w["P1"]["T9"] = 13
    w["P1"]["T10"] = 0

    w["P2"]["T1"] = 68
    w["P2"]["T2"] = 39
    w["P2"]["T3"] = 41
    w["P2"]["T4"] = 39
    w["P2"]["T5"] = 37
    w["P2"]["T6"] = 39
    w["P2"]["T7"] = 16
    w["P2"]["T8"] = 16
    w["P2"]["T9"] = 16
    w["P2"]["T10"] = 0

    w["P3"]["T1"] = 86
    w["P3"]["T2"] = 42
    w["P3"]["T3"] = 43
    w["P3"]["T4"] = 50
    w["P3"]["T5"] = 28
    w["P3"]["T6"] = 44
    w["P3"]["T7"] = 22
    w["P3"]["T8"] = 33
    w["P3"]["T9"] = 20
    w["P3"]["T10"] = 0

    # from earlier page
    w["P1"]["T1"] = 22
    w["P1"]["T2"] = 22
    w["P1"]["T3"] = 32
    w["P1"]["T4"] = 7
    w["P1"]["T5"] = 29
    w["P1"]["T6"] = 26
    w["P1"]["T7"] = 14
    w["P1"]["T8"] = 29
    w["P1"]["T9"] = 15
    w["P1"]["T10"] = 13

    w["P2"]["T1"] = 21
    w["P2"]["T2"] = 18
    w["P2"]["T3"] = 27
    w["P2"]["T4"] = 10
    w["P2"]["T5"] = 27
    w["P2"]["T6"] = 17
    w["P2"]["T7"] = 25
    w["P2"]["T8"] = 23
    w["P2"]["T9"] = 21
    w["P2"]["T10"] = 16

    w["P3"]["T1"] = 36
    w["P3"]["T2"] = 18
    w["P3"]["T3"] = 43
    w["P3"]["T4"] = 4
    w["P3"]["T5"] = 35
    w["P3"]["T6"] = 24
    w["P3"]["T7"] = 30
    w["P3"]["T8"] = 36
    w["P3"]["T9"] = 8
    w["P3"]["T10"] = 33

    succ = {}
    succ["T1"] = ["T2", "T3", "T4", "T5", "T6"]
    succ["T2"] = ["T8", "T9"]
    succ["T3"] = ["T7"]
    succ["T4"] = ["T8", "T9"]
    succ["T5"] = ["T9"]
    succ["T6"] = ["T8"]

    succ["T7"] = ["T10"]
    succ["T8"] = ["T10"]
    succ["T9"] = ["T10"]
    succ["T10"] = []

    data = defaultdict(dict)
    data["T1"]["T2"] = 17
    data["T1"]["T3"] = 31
    data["T1"]["T4"] = 29
    data["T1"]["T5"] = 13
    data["T1"]["T6"] = 7

    data["T2"]["T8"] = 3
    data["T2"]["T9"] = 30

    data["T3"]["T7"] = 16
    data["T4"]["T8"] = 11
    data["T4"]["T9"] = 7
    data["T5"]["T9"] = 57
    data["T6"]["T8"] = 5

    data["T7"]["T10"] = 9
    data["T8"]["T10"] = 42
    data["T9"]["T10"] = 7

    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    rank_d, c_proc_i_j = generate_rank_d(
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
    )

    rank_u_test["T1"] = 169
    rank_u_test["T2"] = 114.3
    rank_u_test["T3"] = 102.7
    rank_u_test["T4"] = 110
    rank_u_test["T5"] = 129.7
    rank_u_test["T6"] = 119.3
    rank_u_test["T7"] = 52.7
    rank_u_test["T8"] = 92
    rank_u_test["T9"] = 42.3
    rank_u_test["T10"] = 20.7

    for task in task_names:
        # print(task, rank_d[task], rank_u_test[task])
        assert math.isclose(rank_d[task], rank_u_test[task], rel_tol=0.01)


def test_allocation_from_heft_paper():
    expected_allocation = defaultdict(list)
    expected_allocation["P3"].extend(["T1", "T3", "T5", "T7"])
    expected_allocation["P2"].extend(["T4", "T6", "T9", "T10"])
    expected_allocation["P1"].extend(["T2", "T8"])
    expected_makespan = 80

    (
        task_names,
        machines,
        machine_types,
        w,
        data,
        rank_u_test,
        succ,
    ) = generate_data_heft_paper()

    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    rank_d, c_proc_i_j = generate_rank_d(
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
    )

    preds = defaultdict(list)
    for pred, succ_el in succ.items():
        for el in succ_el:
            preds[el].append(pred)

    allocation, makespan, _, _ = generate_assignment(
        machines, w, preds, c_proc_i_j, rank_d
    )

    for processor_name in expected_allocation.keys():
        assert expected_allocation[processor_name] == [
            el["name"] for el in allocation[processor_name]
        ]
