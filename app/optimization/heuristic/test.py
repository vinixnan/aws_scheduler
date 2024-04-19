import math
from collections import defaultdict

from optimization.heuristic.base import generate_W_line
from optimization.heuristic.heft import generate_assignment, generate_rank_d
from optimization.heuristic.peft import generate_oct, peft_generate_assignment
from optimization.heuristic.hsip import generate_rank_d_hsip, hsip_generate_assignment
from pysim_helper import Machine


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


def generate_data_peft_paper():
    task_names = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"]
    machines = {"P1": {}, "P2": {}, "P3": {}}
    for m in machines.keys():
        machines[m] = Machine(m, {"name": m}, "link" + m)

    machine_types = list(machines.keys())
    w = defaultdict(dict)
    rank_u_test = {}
    rank_oct_test = {}

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

    rank_oct_test["T1"] = 72.7
    rank_oct_test["T2"] = 41
    rank_oct_test["T3"] = 37
    rank_oct_test["T4"] = 43.7
    rank_oct_test["T5"] = 31
    rank_oct_test["T6"] = 41.7
    rank_oct_test["T7"] = 17
    rank_oct_test["T8"] = 20.7
    rank_oct_test["T9"] = 16.3
    rank_oct_test["T10"] = 0

    return (
        task_names,
        machines,
        machine_types,
        w,
        data,
        rank_u_test,
        rank_oct_test,
        succ,
    )


def test_rank_u_heft_paper():
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
        assert math.isclose(rank_d[task], rank_u_test[task], rel_tol=0.01), (
            task + " " + str(rank_d[task]) + " " + str(rank_u_test[task])
        )


def test_rank_u_peft_paper():
    task_names = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"]
    machines = {"P1": {}, "P2": {}, "P3": {}}
    machine_types = list(machines.keys())

    (
        task_names,
        machines,
        machine_types,
        w,
        data,
        rank_u_test,
        rank_oct_test,
        succ,
    ) = generate_data_peft_paper()

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
        assert math.isclose(rank_d[task], rank_u_test[task], rel_tol=0.01), (
            task + " " + str(rank_d[task]) + " " + str(rank_u_test[task])
        )


def test_rank_oct_peft_paper():
    task_names = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"]
    machines = {"P1": {}, "P2": {}, "P3": {}}
    machine_types = list(machines.keys())

    (
        task_names,
        machines,
        machine_types,
        w,
        data,
        rank_u_test,
        rank_oct_test,
        succ,
    ) = generate_data_peft_paper()

    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    preds = defaultdict(list)
    for pred, succ_el in succ.items():
        for el in succ_el:
            preds[el].append(pred)

    table, rank, c_proc_i_j = generate_oct(
        B_m_n,
        B_m_n_line,
        w_line,
        machines,
        task_names,
        machine_types,
        dataset_machines,
        w,
        succ,
        preds,
        data,
    )

    for task in task_names:
        assert math.isclose(rank[task], rank_oct_test[task], rel_tol=0.01), (
            task + " " + str(rank[task]) + " " + str(rank_oct_test[task])
        )


def test_allocation_from_for_heft_from_heft_paper():
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

    allocation, makespan, _, _ = generate_assignment(machines, w, preds, c_proc_i_j, rank_d)

    for processor_name in expected_allocation.keys():
        assert expected_allocation[processor_name] == [el["name"] for el in allocation[processor_name]], (
            str(expected_allocation[processor_name]) + " " + str([el["name"] for el in allocation[processor_name]])
        )

    assert makespan == expected_makespan


def test_allocation_from_for_peft_from_peft_paper():
    expected_allocation = defaultdict(list)
    expected_allocation["P3"].extend(["T5", "T9"])
    expected_allocation["P2"].extend(["T6", "T8", "T10"])
    expected_allocation["P1"].extend(["T1", "T4", "T2", "T3", "T7"])
    expected_makespan = 122

    expected_oeft = {}
    expected_oeft["T1"] = 86
    expected_oeft["T4"] = 71
    expected_oeft["T6"] = 85
    expected_oeft["T2"] = 93
    expected_oeft["T3"] = 110
    expected_oeft["T5"] = 98
    expected_oeft["T8"] = 93
    expected_oeft["T7"] = 110
    expected_oeft["T9"] = 109
    expected_oeft["T10"] = 122

    (
        task_names,
        machines,
        machine_types,
        w,
        data,
        rank_u_test,
        rank_oct_test,
        succ,
    ) = generate_data_peft_paper()

    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    preds = defaultdict(list)
    for pred, succ_el in succ.items():
        for el in succ_el:
            preds[el].append(pred)

    oct_table, rank_oct, c_proc_i_j = generate_oct(
        B_m_n,
        B_m_n_line,
        w_line,
        machines,
        task_names,
        machine_types,
        dataset_machines,
        w,
        succ,
        preds,
        data,
    )

    allocation, makespan, _, _ = peft_generate_assignment(machines, w, preds, c_proc_i_j, oct_table, rank_oct)

    for processor_name in expected_allocation.keys():
        assert expected_allocation[processor_name] == [el["name"] for el in allocation[processor_name]], (
            str(expected_allocation[processor_name]) + " " + str([el["name"] for el in allocation[processor_name]])
        )

    all_generated_oeft = {}
    for values in allocation.values():
        all_generated_oeft.update({el["name"]: el["OEFT"] for el in values})

    for task_name, expected in expected_oeft.items():
        assert all_generated_oeft[task_name] == expected, str(all_generated_oeft[task_name]) + " " + str(expected)

    assert makespan == expected_makespan


def test_allocation_from_for_heft_from_peft_paper():
    expected_allocation = defaultdict(list)
    expected_allocation["P3"].extend(["T6", "T4", "T9"])
    expected_allocation["P2"].extend(["T1", "T5", "T3", "T7"])
    expected_allocation["P1"].extend(["T2", "T8", "T10"])
    expected_makespan = 133

    (
        task_names,
        machines,
        machine_types,
        w,
        data,
        rank_u_test,
        rank_oct_test,
        succ,
    ) = generate_data_peft_paper()

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

    allocation, makespan, _, _ = generate_assignment(machines, w, preds, c_proc_i_j, rank_d)

    assert makespan == expected_makespan
    for processor_name in expected_allocation.keys():
        assert expected_allocation[processor_name] == [el["name"] for el in allocation[processor_name]], (
            str(expected_allocation[processor_name]) + " " + str([el["name"] for el in allocation[processor_name]])
        )


def test_rank_d_for_hsip_from_heft_paper():
    expected = {}
    expected["T1"] = 335.6
    expected["T2"] = 233.4
    expected["T3"] = 209.6
    expected["T4"] = 229.1
    expected["T5"] = 182.2
    expected["T6"] = 184.7
    expected["T7"] = 137.9
    expected["T8"] = 133.4
    expected["T9"] = 154.6
    expected["T10"] = 85.0

    (
        task_names,
        machines,
        machine_types,
        w,
        data,
        rank_u_test,
        succ,
    ) = generate_data_heft_paper()

    # for some reason the author of HSIP changed 17 by 7. See Figure 1 of the paper.
    w["P3"]["T4"] = 7

    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    preds = defaultdict(list)
    for pred, succ_el in succ.items():
        for el in succ_el:
            preds[el].append(pred)

    dataset_machines = {}

    rank_d, c_proc_i_j = generate_rank_d_hsip(
        B_m_n,
        B_m_n_line,
        w_line,
        machines,
        task_names,
        machine_types,
        dataset_machines,
        w,
        succ,
        preds,
        data,
    )
    print(rank_d)
    for task in task_names:
        assert math.isclose(rank_d[task], expected[task], rel_tol=0.01), (
            task + " " + str(expected[task]) + " " + str(rank_d[task])
        )

    assignment, makespan, first_host, last_host = hsip_generate_assignment(machines, w, preds, c_proc_i_j, rank_d, succ)

    import pdb

    pdb.set_trace()


def el_test():
    print("test_rank_u_heft_paper")
    test_rank_u_heft_paper()
    print("test_allocation_from_for_heft_from_heft_paper")
    test_allocation_from_for_heft_from_heft_paper()
    print("test_rank_u_peft_paper")
    test_rank_u_peft_paper()
    print("test_rank_oct_peft_paper")
    test_rank_oct_peft_paper()
    print("test_allocation_from_for_peft_from_peft_paper")
    test_allocation_from_for_peft_from_peft_paper()
    print("test_allocation_from_for_heft_from_peft_paper")
    test_allocation_from_for_heft_from_peft_paper()
    print("test_rank_d_for_hsip_from_heft_paper")
    test_rank_d_for_hsip_from_heft_paper()
