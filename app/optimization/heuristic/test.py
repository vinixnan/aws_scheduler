import math
from collections import defaultdict

from optimization.heuristic.base import generate_W_line
from optimization.heuristic.heft import generate_assignment, generate_rank_d
from optimization.heuristic.peft import generate_oct, peft_generate_assignment
from optimization.heuristic.hsip import generate_rank_d_hsip, hsip_generate_assignment
from optimization.heuristic.test_datasets import (
    generate_data_heft_paper,
    generate_data_peft_paper,
    generate_data_hsip_paper,
)


def test_rank_u_heft_paper():
    (task_names, machines, machine_types, w, data, rank_u_test, succ, preds) = generate_data_heft_paper()
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
        preds,
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
        preds,
    ) = generate_data_peft_paper()

    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

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
        preds,
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
        preds,
    ) = generate_data_peft_paper()

    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

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
        preds,
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
        preds,
    ) = generate_data_hsip_paper()

    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

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
    for task in task_names:
        assert math.isclose(rank_d[task], expected[task], rel_tol=0.01), (
            task + " " + str(expected[task]) + " " + str(rank_d[task])
        )


def test_allocation_for_hsip_from_hsip_paper():
    expected_makespan = 83

    (
        task_names,
        machines,
        machine_types,
        w,
        data,
        rank_u_test,
        succ,
        preds,
    ) = generate_data_hsip_paper()

    w_line = generate_W_line(w, task_names, machine_types)

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

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

    allocation, makespan, first_host, last_host = hsip_generate_assignment(machines, w, preds, c_proc_i_j, rank_d, succ)
    assert makespan == expected_makespan, str(expected_makespan) + " " + str(makespan)


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
    print("test_allocation_for_hsip_from_hsip_paper")
    test_allocation_for_hsip_from_hsip_paper()
