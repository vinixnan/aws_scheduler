import copy
import math
from collections import OrderedDict, defaultdict, deque

from optimization.heuristic.peft import PEFT


class MPEFT(PEFT):
    def __init__(self, w, dataset_machines, succ, pred, data):
        super().__init__(w, dataset_machines, succ, pred, data)
        self.name = "MPEFT"

    def generate_rank(self, B_m_n, B_m_n_line, w_line, machines, w=None):
        L_m, L_line = self.generate_L(len(machines))
        c_proc_i_j, c_i_j_line = self.generate_C(machines, L_line, B_m_n, B_m_n_line)
        w_min = self.get_all_w_min(w)
        offspring = {}
        for task in self.succ.keys():
            l = []
            self.generate_offspring(task, l)
            offspring[task] = list(set(l))

        dct = self.calc_dct(w_min, c_i_j_line)
        rank_ap = {}
        for task in self.succ.keys():
            to_sum = [0]
            for t in offspring.get(task):
                to_sum.append(dct[t])

            rank_ap[task] = dct[task] + sum(to_sum)

        rank_ap["root"] = float("inf")
        rank_ap["end"] = -1
        rank_ap = OrderedDict(sorted(rank_ap.items(), key=lambda x: x[1], reverse=True))
        return rank_ap, c_proc_i_j, c_i_j_line, self.calc_oct(machines, c_i_j_line)

    def generate_offspring(self, task, l):
        for t in self.succ.get(task, []):
            l.append(t)
            self.generate_offspring(t, l)

    def get_all_w_min(self, w):
        all_w_per_task = defaultdict(list)
        for machine_name, task_data in w.items():
            for task_name, value in task_data.items():
                all_w_per_task[task_name].append(value)

        all_w_min = {}
        for k, values in all_w_per_task.items():
            all_w_min[k] = min(values)

        return all_w_min

    def calc_dct(self, w_min, c_i_j_line):
        dct = {}
        for t in self.succ.keys():
            to_sum = []
            for t2 in self.succ[t]:
                to_sum.append(c_i_j_line[t][t2])
            dct[t] = w_min[t] + sum(to_sum)
        return dct

    def calc_oct(self, machines, c_i_j_line):
        oct_table = defaultdict(dict)
        P = len(machines)

        q = deque([self.last])
        while q:
            current = q.popleft()
            for task_machine in machines:
                self.OCT(current, task_machine, machines, c_i_j_line, oct_table)

            to_add = self.pred[current]
            q.extend(to_add)

        for task_machine in machines:
            oct_table["root"][task_machine] = [0, None]
            oct_table["end"][task_machine] = [0, None]
        return oct_table

    def calc_k_table(self, rank_ap, oct_table, machines, c_i_j_line):
        k_table = defaultdict(dict)
        for t in self.succ.keys():
            if len(self.succ[t]) > len(machines) + 1:
                for task_machine in machines:
                    selected_CPS = oct_table[t][task_machine][1]
                    to_sum = [(rank_ap[t2] + c_i_j_line[t][t2]) for t2 in self.succ[t] if t2 != selected_CPS]
                    if selected_CPS:
                        k_table[t][task_machine] = rank_ap[selected_CPS] / sum(to_sum)
                        print(t, task_machine, selected_CPS, rank_ap[selected_CPS], to_sum, sum(to_sum))
            else:
                for task_machine in machines:
                    k_table[t][task_machine] = 1.0

        return k_table

    def generate_assignment(self, machines, c_proc_i_j, c_i_j_line, rank, oct_table):
        k_table = self.calc_k_table(rank, oct_table, machines, c_i_j_line)
        assignment = defaultdict(list)
        assigned_task = {}
        makespans = {machine_name: 0 for machine_name in machines.keys()}
        for task_id in rank.keys():
            machines_est = {}
            for machine_name, machine_data in machines.items():
                dt = self.calc_EST(task_id, machine_name, assignment, c_proc_i_j, makespans, assigned_task)
                data = {}
                data["EST"] = dt["AFT"]
                data["AFT"] = data["EST"] + self.w[machine_data.data["name"]][task_id]
                data["OEFT"] = data["AFT"] + oct_table[task_id][machine_name][0] * k_table[task_id][machine_name]
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
