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
        return rank_ap, c_proc_i_j, c_i_j_line

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

    def generate_assignment(self, machines, c_proc_i_j, rank, table=None):
        assignment = defaultdict(list)
        assigned_task = {}
        makespans = {machine_name: 0 for machine_name in machines.keys()}

        return assignment, 0, None, None
