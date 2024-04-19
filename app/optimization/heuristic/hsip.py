import math
from collections import OrderedDict, defaultdict, deque
import copy


from optimization.heuristic.base import OCT, calc_EST, generate_C, generate_L


def occw(task, succ, c_i_j_line, memo):
    if memo.get(task):
        return memo[task]

    to_sum = [c_i_j_line[task][suc] for suc in succ[task]]
    to_sum.append(0)
    memo[task] = sum(to_sum)
    return memo[task]


def calc_occw(succ, c_i_j_line):
    succ = OrderedDict(sorted(succ.items(), key=lambda x: len(x[1])))
    occw_table = {}

    for task in succ.keys():
        occw(task, succ, c_i_j_line, occw_table)

    return occw_table


def generate_mean_and_std_table(task_names, machines, w):
    std_dev_table = {}
    mean_table = {}
    multiplied = {}
    for task in task_names:
        all_w_task = [w[machine.data["name"]][task] for machine in machines.values()]
        mean = sum(all_w_task) / len(machines)
        mean_table[task] = mean

        std_dev_table[task] = math.sqrt(
            sum([math.pow(w[machine.data["name"]][task] - mean, 2) for machine in machines.values()]) / len(machines)
        )
        multiplied[task] = mean * std_dev_table[task]

    return mean_table, std_dev_table, multiplied


def recursive_transverse_hsip(task, succ, occw_table, multiplied, memo):
    if memo.get(task):
        return memo[task]

    if not succ[task]:
        memo[task] = multiplied[task] + occw_table[task]
        return memo[task]

    to_see = []
    for suc in succ[task]:
        v = recursive_transverse_hsip(suc, succ, occw_table, multiplied, memo)
        val = v + multiplied[task] + occw_table[task]
        print(task, suc, v, multiplied[task], occw_table[task], val)
        to_see.append(val)

    memo[task] = max(to_see)
    return memo[task]


def generate_rank_d_hsip(
    B_m_n,
    B_m_n_line,
    w_line,
    machines,
    task_names,
    machine_types,
    dataset_machines,
    w,
    succ,
    pred,
    data,
):
    L_m, L_line = generate_L(len(machines))
    c_proc_i_j, c_i_j_line = generate_C(task_names, machines, succ, L_line, data, B_m_n, B_m_n_line)

    occw_table = calc_occw(succ, c_i_j_line)
    mean_table, std_dev_table, multiplied = generate_mean_and_std_table(task_names, machines, w)

    succ = OrderedDict(sorted(succ.items(), key=lambda x: len(x[1])))
    # cuidado
    last = list(succ.keys())[0]
    # cuidado
    q = deque([last])

    rank_d = {}

    while q:
        current = q.popleft()
        recursive_transverse_hsip(current, succ, occw_table, multiplied, rank_d)
        to_add = pred[current]
        q.extend(to_add)

    rank_d = OrderedDict(sorted(rank_d.items(), key=lambda x: x[1], reverse=True))
    return rank_d, c_proc_i_j


def hsip_generate_assignment(machines, w, pred, c_proc_i_j, rank_d, succ):
    no_pred = [task_name for task_name, task_pred in pred.items() if not task_pred]
    entry_task = no_pred[0]
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

    selected = assigned_task[entry_task]["machine"]
    selected_machine_type = assigned_task[entry_task]["machine_type"]["name"]
    other_machines = {
        machine_name: machine_data.data["name"]
        for machine_name, machine_data in machines.items()
        if machine_name != selected
    }
    for other_machine_name, other_machine_type in other_machines.items():
        for suc in succ[entry_task]:
            c_i_j_to_suc = c_proc_i_j[entry_task][suc][other_machine_type][assigned_task[suc]["machine"]]

            if w[selected_machine_type][entry_task] < w[other_machine_type][entry_task] + c_i_j_to_suc:
                data = copy.deepcopy(assigned_task[entry_task])
                data["machine"] = other_machine_name
                data["machine_type"] = machines[other_machine_name].data
                assignment[other_machine_name].append(data)

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
