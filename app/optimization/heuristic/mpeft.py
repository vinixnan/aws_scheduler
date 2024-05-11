import copy
import math
from collections import OrderedDict, defaultdict, deque

from optimization.heuristic.base import Heuristic


class MPEFT(Heuristic):
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
        return rank_ap, c_proc_i_j, None

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

    def generate_assignment(self, machines, c_proc_i_j, rank, table=None):
        assignment = defaultdict(list)
        assigned_task = {}
        makespans = {machine_name: 0 for machine_name in machines.keys()}

        return assignment, 0, None, None
