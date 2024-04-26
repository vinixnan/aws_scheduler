from collections import defaultdict

from utils.definitions import Machine


def generate_data_heft_paper():
    task_names = ["root", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "end"]
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
    w["P1"]["root"] = 0
    w["P1"]["end"] = 0

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
    w["P2"]["root"] = 0
    w["P2"]["end"] = 0

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
    w["P3"]["root"] = 0
    w["P3"]["end"] = 0

    succ = {}
    succ["root"] = ["T1"]
    succ["T1"] = ["T2", "T3", "T4", "T5", "T6"]
    succ["T2"] = ["T8", "T9"]
    succ["T3"] = ["T7"]
    succ["T4"] = ["T8", "T9"]
    succ["T5"] = ["T9"]
    succ["T6"] = ["T8"]

    succ["T7"] = ["T10"]
    succ["T8"] = ["T10"]
    succ["T9"] = ["T10"]
    succ["T10"] = ["end"]
    succ["end"] = []

    data = defaultdict(dict)
    data["root"]["T1"] = 0
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
    data["T10"]["end"] = 0

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
    rank_u_test["root"] = float("inf")
    rank_u_test["end"] = -1

    preds = defaultdict(list)
    for pred, succ_el in succ.items():
        for el in succ_el:
            preds[el].append(pred)

    preds["root"] = []
    return task_names, machines, machine_types, w, data, rank_u_test, succ, preds


def generate_data_peft_paper():
    task_names = ["root", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "end"]
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
    w["P1"]["root"] = 0
    w["P1"]["end"] = 0

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
    w["P2"]["root"] = 0
    w["P2"]["end"] = 0

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
    w["P3"]["root"] = 0
    w["P3"]["end"] = 0

    succ = {}
    succ["root"] = ["T1"]
    succ["T1"] = ["T2", "T3", "T4", "T5", "T6"]
    succ["T2"] = ["T8", "T9"]
    succ["T3"] = ["T7"]
    succ["T4"] = ["T8", "T9"]
    succ["T5"] = ["T9"]
    succ["T6"] = ["T8"]

    succ["T7"] = ["T10"]
    succ["T8"] = ["T10"]
    succ["T9"] = ["T10"]
    succ["T10"] = ["end"]
    succ["end"] = []

    data = defaultdict(dict)
    data["root"]["T1"] = 0
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
    data["T10"]["end"] = 0

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
    rank_u_test["root"] = float("inf")
    rank_u_test["end"] = -1

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
    rank_oct_test["root"] = float("inf")
    rank_oct_test["end"] = -1

    preds = defaultdict(list)
    for pred, succ_el in succ.items():
        for el in succ_el:
            preds[el].append(pred)

    preds["root"] = []

    return (task_names, machines, machine_types, w, data, rank_u_test, rank_oct_test, succ, preds)


def generate_data_hsip_paper():
    (task_names, machines, machine_types, w, data, rank_u_test, succ, preds) = generate_data_heft_paper()
    # for some reason the author of HSIP changed 17 by 7. See Figure 1 of the paper.
    w["P3"]["T4"] = 7
    return task_names, machines, machine_types, w, data, rank_u_test, succ, preds
