import math
from collections import defaultdict

import pytest
from optimization.heuristic.heft import HEFT
from optimization.heuristic.hsip import HSIP
from optimization.heuristic.mpeft import MPEFT
from optimization.heuristic.peft import PEFT
from tests.datasets import (
    generate_data_heft_paper,
    generate_data_hsip_paper,
    generate_data_m_peft_paper,
    generate_data_peft_paper,
)


def test_rank_u_heft_paper():
    (task_names, machines, machine_types, w, data, rank_u_test, succ, preds) = generate_data_heft_paper()

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = HEFT(w, dataset_machines, succ, preds, data)
    w_line = heu.generate_W_line(machine_types)

    rank_d, c_proc_i_j, _, _ = heu.generate_rank(B_m_n, B_m_n_line, w_line, machines)

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

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = HEFT(w, dataset_machines, succ, preds, data)
    w_line = heu.generate_W_line(machine_types)

    rank_d, c_proc_i_j, _, _ = heu.generate_rank(B_m_n, B_m_n_line, w_line, machines)
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

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = PEFT(w, dataset_machines, succ, preds, data)
    w_line = heu.generate_W_line(machine_types)

    rank, c_proc_i_j, _, _ = heu.generate_rank(B_m_n, B_m_n_line, w_line, machines)

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

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = HEFT(w, dataset_machines, succ, preds, data)

    allocation, makespan, _, _ = heu.schedule_with_data(machine_types, machines, B_m_n_line, B_m_n)

    for processor_name in expected_allocation.keys():
        alloc = [el["name"] for el in allocation[processor_name] if el["name"] not in ["root", "end"]]
        assert expected_allocation[processor_name] == alloc, str(expected_allocation[processor_name]) + " " + str(alloc)

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

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = PEFT(w, dataset_machines, succ, preds, data)

    allocation, makespan, _, _ = heu.schedule_with_data(machine_types, machines, B_m_n_line, B_m_n)

    for processor_name in expected_allocation.keys():
        alloc = [el["name"] for el in allocation[processor_name] if el["name"] not in ["root", "end"]]
        assert expected_allocation[processor_name] == alloc, str(expected_allocation[processor_name]) + " " + str(alloc)

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

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = HEFT(w, dataset_machines, succ, preds, data)

    allocation, makespan, _, _ = heu.schedule_with_data(machine_types, machines, B_m_n_line, B_m_n)

    assert makespan == expected_makespan
    for processor_name in expected_allocation.keys():
        alloc = [el["name"] for el in allocation[processor_name] if el["name"] not in ["root", "end"]]
        assert expected_allocation[processor_name] == alloc, str(expected_allocation[processor_name]) + " " + str(alloc)


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
    expected["root"] = float("inf")
    expected["end"] = -1

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

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = HSIP(w, dataset_machines, succ, preds, data)
    w_line = heu.generate_W_line(machine_types)

    rank_d, c_proc_i_j, _, _ = heu.generate_rank(B_m_n, B_m_n_line, w_line, machines)

    for task in task_names:
        assert math.isclose(rank_d[task], expected[task], rel_tol=0.01), (
            task + " " + str(expected[task]) + " " + str(rank_d[task])
        )


def test_allocation_for_hsip_from_hsip_paper():
    expected_makespan = 76

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

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = HSIP(w, dataset_machines, succ, preds, data)

    allocation, makespan, _, _ = heu.schedule_with_data(machine_types, machines, B_m_n_line, B_m_n)

    assert makespan == expected_makespan, str(expected_makespan) + " " + str(makespan)


def test_rank_ap_mpeft_paper():
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
        oct_table,
        cps_table,
        k_table,
    ) = generate_data_m_peft_paper()

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = MPEFT(w, dataset_machines, succ, preds, data)
    w_line = heu.generate_W_line(machine_types)

    rank_d, c_proc_i_j, c_i_j_line, table = heu.generate_rank(B_m_n, B_m_n_line, w_line, machines, w)
    for task in task_names:
        assert math.isclose(rank_d[task], rank_u_test[task], rel_tol=0.01), (
            task + " " + str(rank_d[task]) + " " + str(rank_u_test[task])
        )

    found_oct_table = heu.calc_oct(machines, c_i_j_line)
    for task in task_names:
        for m in machines.keys():
            assert math.isclose(found_oct_table[task][m][0], oct_table[task][m], rel_tol=0.01), (
                task + " " + str(found_oct_table[task][m][0]) + " " + str(oct_table[task][m])
            )

    for task in task_names:
        for m in machines.keys():
            print(task, m, found_oct_table[task][m][1], cps_table[task][m])
            assert found_oct_table[task][m][1] == cps_table[task][m]

    generated_k_table = heu.calc_k_table(rank_d, found_oct_table, machines, c_i_j_line)
    print("generated", generated_k_table)
    for task in task_names:
        for m in machines.keys():
            print(task, m)
            if task != "root":
                assert math.isclose(generated_k_table[task][m], k_table[task][m], rel_tol=0.01), (
                    task + " " + str(generated_k_table[task][m]) + " " + str(k_table[task][m])
                )


def test_allocation_from_for_mpeft_from_mpeft_paper():
    expected_allocation = defaultdict(list)
    expected_allocation["P3"].extend(["T1", "T2", "T6"])
    expected_allocation["P2"].extend(["T4", "T5", "T9", "T8", "T10"])
    expected_allocation["P1"].extend(["T3", "T7"])
    expected_makespan = 73

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
        oct_table,
        cps_table,
        k_table,
    ) = generate_data_m_peft_paper()

    B_m_n_line = 1
    B_m_n = {machine_name: 1 for machine_name in machine_types}

    dataset_machines = {}

    heu = MPEFT(w, dataset_machines, succ, preds, data)

    allocation, makespan, _, _ = heu.schedule_with_data(machine_types, machines, B_m_n_line, B_m_n)

    assert makespan == expected_makespan
    for processor_name in expected_allocation.keys():
        alloc = [el["name"] for el in allocation[processor_name] if el["name"] not in ["root", "end"]]
        assert expected_allocation[processor_name] == alloc, str(expected_allocation[processor_name]) + " " + str(alloc)
