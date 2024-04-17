from collections import defaultdict, OrderedDict
from optimization.heuristic.base import recursive_transverse, calc_EST, generate_L, generate_C, generate_W, generate_B

def generate_rank_d(w_line, machines, task_names, machine_types, dataset_machines, w, graph, succ, data):
    L_m, L_line = generate_L(len(machines))

    B_m_n, B_m_n_line = generate_B(dataset_machines, machine_types, machines)

    c_proc_i_j, c_i_j_line = generate_C(graph, machines, succ, L_line, data, B_m_n, B_m_n_line)
    

    succ = OrderedDict(sorted(succ.items(), key=lambda x: len(x[1])))
    rank_d = {}
    for task in succ.keys():
        recursive_transverse(task, succ, c_i_j_line, w_line, rank_d)

    rank_d = OrderedDict(sorted(rank_d.items(), key=lambda x: x[1], reverse=True))
    return rank_d, c_proc_i_j


def generate_assignment(machines, dc_machines_task_time, pred, c_proc_i_j, rank_d):
    assignment = defaultdict(list)
    assigned_task = {}
    for task_id in rank_d.keys():
        machines_est = {}
        for machine_name, machine_data in machines.items():
            dt = calc_EST(
                task_id, machine_name, assignment, pred, c_proc_i_j, assigned_task
            )
            machines_est[machine_name] = dt["AFT"]

        machines_est = OrderedDict(sorted(machines_est.items(), key=lambda x: x[1]))
        selected = list(machines_est.keys())[0]
        selected_machine_type = machines[selected].data
        data = {}
        data["machine"] = selected
        data["machine_type"] = selected_machine_type
        data["EST"] = machines_est[selected]
        data["AFT"] = (
            data["EST"] + dc_machines_task_time[selected_machine_type['name']][task_id]
        )
        data['name'] = task_id
        assigned_task[task_id] = data
        # c_i_j aqui eh o sem media
        assignment[selected].append(data)

    last_host = None
    makespan = 0
    for host_name, l in assignment.items():
        data = l[-1]
        print(data)
        if data['AFT'] > makespan:
            makespan = data['AFT']
            last_host = host_name

    assignment[last_host].append({'machine':last_host, 'name':'end', 'AFT':assignment[last_host][-1], 'EST':assignment[last_host][-1]})
    assignment[last_host].insert(0, {'machine':last_host, 'name':'root', 'AFT':0, 'EST':0})
    return assignment, makespan, last_host