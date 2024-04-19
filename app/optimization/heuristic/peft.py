from collections import OrderedDict, defaultdict, deque

from optimization.heuristic.base import OCT, calc_EST, generate_C, generate_L


def generate_oct(
    B_m_n,
    B_m_n_line,
    w_line,
    machines,
    task_names,
    machine_types,
    dataset_machines,
    wx,
    succ,
    pred,
    data,
):
    L_m, L_line = generate_L(len(machines))
    c_proc_i_j, c_i_j_line = generate_C(task_names, machines, succ, L_line, data, B_m_n, B_m_n_line)

    oct_table = defaultdict(dict)
    rank_oct = {}
    P = len(machines)

    succ = OrderedDict(sorted(succ.items(), key=lambda x: len(x[1])))
    # cuidado
    last = list(succ.keys())[0]
    # cuidado
    q = deque([last])

    while q:
        current = q.popleft()
        for task_machine in machines:
            OCT(current, task_machine, machines, succ, c_i_j_line, wx, oct_table)

        to_add = pred[current]
        q.extend(to_add)

    rank_oct = {task_name: (sum([v for v in values.values()]) / P) for task_name, values in oct_table.items()}
    rank_oct = OrderedDict(sorted(rank_oct.items(), key=lambda x: x[1], reverse=True))

    return oct_table, rank_oct, c_proc_i_j


def peft_generate_assignment(machines, w, pred, c_proc_i_j, oct_table, rank_oct):
    assignment = defaultdict(list)
    assigned_task = {}
    for task_id in rank_oct.keys():
        machines_est = {}
        for machine_name, machine_data in machines.items():
            dt = calc_EST(task_id, machine_name, assignment, pred, c_proc_i_j, assigned_task)
            data = {}
            data["EST"] = dt["AFT"]
            data["AFT"] = data["EST"] + w[machine_data.data["name"]][task_id]
            data["OEFT"] = data["AFT"] + oct_table[task_id][machine_name]
            data["machine"] = machine_name
            data["name"] = task_id
            machines_est[machine_name] = data

        machines_est = OrderedDict(sorted(machines_est.items(), key=lambda x: x[1]["OEFT"]))
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
