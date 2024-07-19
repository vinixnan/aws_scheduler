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


def generate_data_ppts_paper():
    task_names, machines, machine_types, w, data, rank_u_test, rank_oct_test, succ, preds = generate_data_peft_paper()
    rank_pcm = {}
    rank_pcm["T1"] = 154.3
    rank_pcm["T2"] = 98
    rank_pcm["T3"] = 96.3
    rank_pcm["T4"] = 92.7
    rank_pcm["T5"] = 90.7
    rank_pcm["T6"] = 98.3
    rank_pcm["T7"] = 46
    rank_pcm["T8"] = 69
    rank_pcm["T9"] = 45.7
    rank_pcm["T10"] = 20.7
    rank_pcm["root"] = float("inf")
    rank_pcm["end"] = -1
    return (task_names, machines, machine_types, w, data, rank_u_test, rank_oct_test, rank_pcm, succ, preds)


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


def generate_data_m_peft_paper():
    task_names = ["root", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "end"]
    machines = {"P1": {}, "P2": {}, "P3": {}}
    for m in machines.keys():
        machines[m] = Machine(m, {"name": m}, "link" + m)

    machine_types = list(machines.keys())
    w = defaultdict(dict)
    rank_u_test = {}
    rank_oct_test = {}

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

    rank_u_test["T1"] = 332
    rank_u_test["T2"] = 96
    rank_u_test["T3"] = 65
    rank_u_test["T4"] = 106
    rank_u_test["T5"] = 55
    rank_u_test["T6"] = 47
    rank_u_test["T7"] = 31
    rank_u_test["T8"] = 23
    rank_u_test["T9"] = 32
    rank_u_test["T10"] = 7
    rank_u_test["root"] = float("inf")
    rank_u_test["end"] = -1

    oct_table = defaultdict(dict)
    oct_table["T1"]["P1"] = 48
    oct_table["T2"]["P1"] = 35
    oct_table["T3"]["P1"] = 28
    oct_table["T4"]["P1"] = 38
    oct_table["T5"]["P1"] = 32
    oct_table["T6"]["P1"] = 23
    oct_table["T7"]["P1"] = 21
    oct_table["T8"]["P1"] = 18
    oct_table["T9"]["P1"] = 20
    oct_table["T10"]["P1"] = 0
    oct_table["root"]["P1"] = 0
    oct_table["end"]["P1"] = 0

    oct_table["T1"]["P2"] = 38
    oct_table["T2"]["P2"] = 19
    oct_table["T3"]["P2"] = 22
    oct_table["T4"]["P2"] = 19
    oct_table["T5"]["P2"] = 19
    oct_table["T6"]["P2"] = 18
    oct_table["T7"]["P2"] = 7
    oct_table["T8"]["P2"] = 7
    oct_table["T9"]["P2"] = 7
    oct_table["T10"]["P2"] = 0
    oct_table["root"]["P2"] = 0
    oct_table["end"]["P2"] = 0

    oct_table["T1"]["P3"] = 53
    oct_table["T2"]["P3"] = 35
    oct_table["T3"]["P3"] = 27
    oct_table["T4"]["P3"] = 36
    oct_table["T5"]["P3"] = 32
    oct_table["T6"]["P3"] = 30
    oct_table["T7"]["P3"] = 16
    oct_table["T8"]["P3"] = 16
    oct_table["T9"]["P3"] = 16
    oct_table["T10"]["P3"] = 0
    oct_table["root"]["P3"] = 0
    oct_table["end"]["P3"] = 0

    cps_table = defaultdict(dict)
    cps_table["T1"]["P1"] = "T2"
    cps_table["T2"]["P1"] = "T9"
    cps_table["T3"]["P1"] = "T7"
    cps_table["T4"]["P1"] = "T9"
    cps_table["T5"]["P1"] = "T9"
    cps_table["T6"]["P1"] = "T8"
    cps_table["T7"]["P1"] = "T10"
    cps_table["T8"]["P1"] = "T10"
    cps_table["T9"]["P1"] = "T10"
    cps_table["T10"]["P1"] = "end"
    cps_table["root"]["P1"] = None
    cps_table["end"]["P1"] = None

    cps_table["T1"]["P2"] = "T2"
    cps_table["T2"]["P2"] = "T9"
    cps_table["T3"]["P2"] = "T7"
    cps_table["T4"]["P2"] = "T9"
    cps_table["T5"]["P2"] = "T9"
    cps_table["T6"]["P2"] = "T8"
    cps_table["T7"]["P2"] = "T10"
    cps_table["T8"]["P2"] = "T10"
    cps_table["T9"]["P2"] = "T10"
    cps_table["T10"]["P2"] = "end"
    cps_table["root"]["P2"] = None
    cps_table["end"]["P2"] = None

    cps_table["T1"]["P3"] = "T2"
    cps_table["T2"]["P3"] = "T9"
    cps_table["T3"]["P3"] = "T7"
    cps_table["T4"]["P3"] = "T9"
    cps_table["T5"]["P3"] = "T9"
    cps_table["T6"]["P3"] = "T8"
    cps_table["T7"]["P3"] = "T10"
    cps_table["T8"]["P3"] = "T10"
    cps_table["T9"]["P3"] = "T10"
    cps_table["T10"]["P3"] = "end"
    cps_table["root"]["P3"] = None
    cps_table["end"]["P3"] = None

    k_table = defaultdict(dict)
    for task, ms in cps_table.items():
        for m in ms.keys():
            k_table[task][m] = 1

    k_table["T1"]["P1"] = 0.3
    k_table["T1"]["P2"] = 0.3
    k_table["T1"]["P3"] = 0.3

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

    return (
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
    )


def generate_data_ippts_paper():
    task_names = ["root", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "end"]
    machines = {"P1": {}, "P2": {}, "P3": {}}
    for m in machines.keys():
        machines[m] = Machine(m, {"name": m}, "link" + m)

    machine_types = list(machines.keys())
    w = defaultdict(dict)
    p_rank = {}

    w["P1"]["T1"] = 64
    w["P1"]["T2"] = 2
    w["P1"]["T3"] = 7
    w["P1"]["T4"] = 27
    w["P1"]["T5"] = 84
    w["P1"]["T6"] = 10
    w["P1"]["T7"] = 48
    w["P1"]["T8"] = 26
    w["P1"]["T9"] = 21
    w["P1"]["T10"] = 10
    w["P1"]["root"] = 0
    w["P1"]["end"] = 0

    w["P2"]["T1"] = 26
    w["P2"]["T2"] = 4
    w["P2"]["T3"] = 17
    w["P2"]["T4"] = 29
    w["P2"]["T5"] = 68
    w["P2"]["T6"] = 52
    w["P2"]["T7"] = 37
    w["P2"]["T8"] = 77
    w["P2"]["T9"] = 20
    w["P2"]["T10"] = 4
    w["P2"]["root"] = 0
    w["P2"]["end"] = 0

    w["P3"]["T1"] = 18
    w["P3"]["T2"] = 16
    w["P3"]["T3"] = 9
    w["P3"]["T4"] = 43
    w["P3"]["T5"] = 17
    w["P3"]["T6"] = 87
    w["P3"]["T7"] = 8
    w["P3"]["T8"] = 75
    w["P3"]["T9"] = 5
    w["P3"]["T10"] = 11
    w["P3"]["root"] = 0
    w["P3"]["end"] = 0

    succ = {}
    succ["root"] = ["T1"]
    succ["T1"] = ["T2", "T3", "T4"]
    succ["T2"] = ["T5"]
    succ["T3"] = ["T6"]
    succ["T4"] = ["T7"]
    succ["T5"] = ["T8"]
    succ["T6"] = ["T9"]
    succ["T7"] = ["T9"]
    succ["T8"] = ["T10"]
    succ["T9"] = ["T10"]
    succ["T10"] = ["end"]
    succ["end"] = []

    data = defaultdict(dict)
    data["root"]["T1"] = 0
    data["T1"]["T2"] = 43
    data["T1"]["T3"] = 89
    data["T1"]["T4"] = 34

    data["T2"]["T5"] = 85
    data["T3"]["T6"] = 67
    data["T4"]["T7"] = 58

    data["T5"]["T8"] = 46
    data["T6"]["T9"] = 63
    data["T7"]["T9"] = 59

    data["T8"]["T10"] = 77
    data["T9"]["T10"] = 19
    data["T10"]["end"] = 0

    p_rank["T1"] = 854
    p_rank["T2"] = 246
    p_rank["T3"] = 133.67
    p_rank["T4"] = 129.67
    p_rank["T5"] = 182.33
    p_rank["T6"] = 97
    p_rank["T7"] = 74.67
    p_rank["T8"] = 76
    p_rank["T9"] = 32
    p_rank["T10"] = 0
    p_rank["root"] = float("inf")
    p_rank["end"] = -1

    # p_rank["T10"] = 8.333

    PCM = defaultdict(dict)
    PCM["P1"]["T1"] = 299
    PCM["P1"]["T2"] = 242
    PCM["P1"]["T3"] = 89
    PCM["P1"]["T4"] = 149
    PCM["P1"]["T5"] = 156
    PCM["P1"]["T6"] = 72
    PCM["P1"]["T7"] = 99
    PCM["P1"]["T8"] = 46
    PCM["P1"]["T9"] = 41
    PCM["P1"]["T10"] = 10

    PCM["P2"]["T1"] = 299
    PCM["P2"]["T2"] = 274
    PCM["P2"]["T3"] = 156
    PCM["P2"]["T4"] = 149
    PCM["P2"]["T5"] = 202
    PCM["P2"]["T6"] = 100
    PCM["P2"]["T7"] = 85
    PCM["P2"]["T8"] = 85
    PCM["P2"]["T9"] = 28
    PCM["P2"]["T10"] = 4

    PCM["P3"]["T1"] = 256
    PCM["P3"]["T2"] = 222
    PCM["P3"]["T3"] = 156
    PCM["P3"]["T4"] = 91
    PCM["P3"]["T5"] = 189
    PCM["P3"]["T6"] = 119
    PCM["P3"]["T7"] = 40
    PCM["P3"]["T8"] = 97
    PCM["P3"]["T9"] = 27
    PCM["P3"]["T10"] = 11

    preds = defaultdict(list)
    for pred, succ_el in succ.items():
        for el in succ_el:
            preds[el].append(pred)

    preds["root"] = []
    return task_names, machines, machine_types, w, data, p_rank, succ, preds, PCM
