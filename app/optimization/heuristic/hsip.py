import copy
import math
from collections import OrderedDict, defaultdict, deque

from optimization.heuristic.base import Heuristic


class HSIP(Heuristic):
    def __init__(self, w, dataset_machines, succ, pred, data):
        super().__init__(w, dataset_machines, succ, pred, data)
        self.name = "HSIP"

    def calc_EST(self, task, task_machine, assignment, c_proc_i_j, makespans, memo):
        if memo.get(task):
            return memo[task]

        values = []
        for t in self.pred.get(task, []):
            data = self.calc_EST(t, task_machine, assignment, c_proc_i_j, makespans, memo)
            if not isinstance(data, list):
                cj = c_proc_i_j[t][task][data["machine"]][task_machine]
                val = data["AFT"] + cj
                values.append(val)
            else:
                find_min = []

                for d in data:
                    cj = c_proc_i_j[t][task][d["machine"]][task_machine]
                    val = d["AFT"] + cj
                    find_min.append(val)
                mi = min(find_min)
                values.append(mi)

        to_return = 0
        if values:
            to_return = max(values)

        data = {}
        data["AFT"] = to_return
        machine_assignment = assignment[task_machine]
        if machine_assignment:
            if makespans[task_machine]["AFT"] > to_return:
                data = makespans[task_machine]

        return data

    def occw(self, task, c_i_j_line, memo):
        if memo.get(task):
            return memo[task]

        to_sum = [c_i_j_line[task][suc] for suc in self.succ[task]]
        to_sum.append(0)
        memo[task] = sum(to_sum)
        return memo[task]

    def calc_occw(self, c_i_j_line):
        occw_table = {}

        for task in self.succ.keys():
            self.occw(task, c_i_j_line, occw_table)

        return occw_table

    def generate_mean_and_std_table(self, machines):
        std_dev_table = {}
        mean_table = {}
        multiplied = {}
        for task in self.task_names:
            all_w_task = [self.w[machine.data["name"]][task] for machine in machines.values()]
            mean = sum(all_w_task) / len(machines)
            mean_table[task] = mean

            std_dev_table[task] = math.sqrt(
                sum([math.pow(self.w[machine.data["name"]][task] - mean, 2) for machine in machines.values()])
                / len(machines)
            )
            multiplied[task] = mean * std_dev_table[task]

        return mean_table, std_dev_table, multiplied

    def recursive_transverse_hsip(self, task, occw_table, multiplied, memo):
        if memo.get(task):
            return memo[task]

        if not self.succ[task]:
            memo[task] = multiplied[task] + occw_table[task]
            return memo[task]

        to_see = []
        for suc in self.succ[task]:
            v = self.recursive_transverse_hsip(suc, occw_table, multiplied, memo)
            val = v + multiplied[task] + occw_table[task]
            to_see.append(val)

        memo[task] = max(to_see)
        return memo[task]

    def generate_rank(self, B_m_n, B_m_n_line, w_line, machines, w=None):
        L_m, L_line = self.generate_L(len(machines))
        c_proc_i_j, c_i_j_line = self.generate_C(machines, L_line, B_m_n, B_m_n_line)

        occw_table = self.calc_occw(c_i_j_line)
        mean_table, std_dev_table, multiplied = self.generate_mean_and_std_table(machines)

        q = deque([self.last])

        rank_d = {}

        while q:
            current = q.popleft()
            self.recursive_transverse_hsip(current, occw_table, multiplied, rank_d)
            to_add = self.pred[current]
            q.extend(to_add)

        rank_d["root"] = float("inf")
        rank_d["end"] = -1
        rank_d = OrderedDict(sorted(rank_d.items(), key=lambda x: x[1], reverse=True))
        return rank_d, c_proc_i_j, c_i_j_line, None

    def entry_node_rule(
        self, entry_task, selected, machines, assigned_task, c_proc_i_j, assignment, machines_est, makespans
    ):
        selected_machine = selected["machine"]
        selected_machine_type = selected["machine_type"]["name"]
        other_machines = {
            machine_name: machine_data.data["name"]
            for machine_name, machine_data in machines.items()
            if machine_name != selected_machine
        }
        for other_machine_name, other_machine_type in other_machines.items():
            for suc in self.succ[entry_task]:
                machines_names = [el["machine"] for el in assigned_task[entry_task]]
                if other_machine_name in machines_names:
                    continue

                c_i_j_to_suc = c_proc_i_j[entry_task][suc][selected_machine][other_machine_name]

                if self.w[selected_machine_type][entry_task] < self.w[other_machine_type][entry_task] + c_i_j_to_suc:
                    data = machines_est[other_machine_name]
                    data["machine_type"] = machines[other_machine_name].data
                    assignment[other_machine_name].append(data)
                    assigned_task[entry_task].append(data)
                    makespans[other_machine_name] = data

    def generate_assignment(self, machines, c_proc_i_j, c_i_j_line, rank_d, table=None):
        no_pred = [task_name for task_name, task_pred in self.pred.items() if not task_pred]
        entry_task = no_pred[0]
        assignment = defaultdict(list)
        assigned_task = {}
        makespans = {machine_name: 0 for machine_name in machines.keys()}
        # special processing for entry
        task_id = entry_task
        machines_est = {}
        for machine_name, machine_data in machines.items():
            dt = self.calc_EST(task_id, machine_name, assignment, c_proc_i_j, makespans, assigned_task)
            data = {}
            data["EST"] = 0
            data["AFT"] = data["EST"] + self.w[machine_data.data["name"]][task_id]
            data["machine"] = machine_name
            data["name"] = task_id
            machines_est[machine_name] = data

        machines_est = OrderedDict(sorted(machines_est.items(), key=lambda x: x[1]["AFT"]))
        selected = list(machines_est.keys())[0]

        selected_data = machines_est[selected]
        selected_machine_type = machines[selected].data
        selected_data["machine_type"] = selected_machine_type

        l = assigned_task.get(task_id, [])
        l.append(selected_data)
        assigned_task[task_id] = l
        assignment[selected].append(selected_data)
        makespans[selected] = selected_data
        self.entry_node_rule(
            entry_task, selected_data, machines, assigned_task, c_proc_i_j, assignment, machines_est, makespans
        )

        del rank_d[entry_task]
        # end - special processing for entry
        for task_id in rank_d.keys():
            machines_est = {}
            for machine_name, machine_data in machines.items():
                dt = self.calc_EST(task_id, machine_name, assignment, c_proc_i_j, makespans, assigned_task)
                data = {}
                data["EST"] = dt["AFT"]
                data["AFT"] = data["EST"] + self.w[machine_data.data["name"]][task_id]
                data["w"] = self.w[machine_data.data["name"]][task_id]
                data["machine"] = machine_name
                data["name"] = task_id
                machines_est[machine_name] = data

            machines_est = OrderedDict(sorted(machines_est.items(), key=lambda x: (x[1]["AFT"], x[1]["w"])))
            selected = list(machines_est.keys())[0]

            selected_data = machines_est[selected]
            selected_machine_type = machines[selected].data
            selected_data["machine_type"] = selected_machine_type

            assigned_task[task_id] = selected_data
            assignment[selected].append(selected_data)
            makespans[selected] = selected_data

        last_host = None
        first_host = None
        makespan = 0
        for host_name, l in assignment.items():
            if l:
                data = l[-1]
                if data["AFT"] > makespan:
                    makespan = data["AFT"]
                    last_host = host_name
                data = l[0]
                if data["EST"] == 0:
                    first_host = host_name

        return assignment, makespan, first_host, last_host
