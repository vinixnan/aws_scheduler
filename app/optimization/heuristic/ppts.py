from collections import OrderedDict, defaultdict

from optimization.heuristic.base import Heuristic


class PPTS(Heuristic):
    def __init__(self, w, dataset_machines, succ, pred, data):
        super().__init__(w, dataset_machines, succ, pred, data)
        self.name = "PPTS"

    def recursive_transverse(self, task, c_i_j_line, w_line, w, p_task, PCM):
        if PCM[p_task].get(task):
            return PCM[p_task][task]

        if not self.succ[task] or self.succ[task][0] == "end":
            PCM[p_task][task] = w[p_task][task]
            return PCM[p_task][task]

        to_see = []
        for suc in self.succ[task]:
            find_min = []
            for suc_p in w.keys():
                c = 0
                if suc_p != p_task:
                    c = c_i_j_line[task][suc]
                w_val = w[suc_p][task] + w[suc_p][suc] + c
                from_rec = self.recursive_transverse(suc, c_i_j_line, w_line, w, suc_p, PCM)
                val = from_rec + w_val
                find_min.append(val)
            to_see.append(min(find_min))

        PCM[p_task][task] = max(to_see)
        return PCM[p_task][task]

    def rank_calc(self, value, qtd_processors, task_name=None):
        return value / qtd_processors

    def generate_rank(self, B_m_n, B_m_n_line, w_line, machines, w):
        L_m, L_line = self.generate_L(len(machines))
        c_proc_i_j, c_i_j_line = self.generate_C(machines, L_line, B_m_n, B_m_n_line)
        PCM = defaultdict(dict)
        for p in w.keys():
            for task in self.succ.keys():
                self.recursive_transverse(task, c_i_j_line, w_line, w, p, PCM)

        for p in w.keys():
            PCM[p]["root"] = 0
            PCM[p]["end"] = 0

        rank_pcm = {}
        for task in self.succ.keys():
            to_sum = 0
            for p in w.keys():
                to_sum = to_sum + PCM[p][task]

            rank_pcm[task] = self.rank_calc(to_sum, len(w.keys()), task)

        rank_pcm["root"] = float("inf")
        rank_pcm["end"] = -1

        rank_pcm = OrderedDict(sorted(rank_pcm.items(), key=lambda x: x[1], reverse=True))
        return rank_pcm, c_proc_i_j, c_i_j_line, PCM

    def generate_assignment(self, machines, c_proc_i_j, c_i_j_line, rank, table):
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
                data["LA_EFT"] = data["AFT"] + table[machine_name][task_id]
                data["machine"] = machine_name
                data["name"] = task_id
                machines_est[machine_name] = data

            machines_est = OrderedDict(sorted(machines_est.items(), key=lambda x: x[1]["LA_EFT"]))
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


class IPPTS(PPTS):
    def __init__(self, w, dataset_machines, succ, pred, data):
        super().__init__(w, dataset_machines, succ, pred, data)
        self.name = "IPPTS"

    def rank_calc(self, value, qtd_processors, task_name):
        # because we decided to always put the end after P10, thus we have to consider T10 has outd as 1 and not as 0 (no sucessor).
        # For this reason the test is changed to 8.333 * 1 (instead of 8.333 * 0)
        mult = len(self.succ[task_name])
        if mult == 1 and self.succ[task_name][0] == "end":
            mult = 0

        return value / qtd_processors * mult

    def generate_assignment(self, machines, c_proc_i_j, c_i_j_line, rank, table):
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
                # this two lines are different from PPTS
                data["LHET"] = table[machine_name][task_id] - self.w[machine_data.data["name"]][task_id]
                data["LA_EFT"] = data["AFT"] + data["LHET"]
                #
                data["machine"] = machine_name
                data["name"] = task_id
                machines_est[machine_name] = data

            machines_est = OrderedDict(sorted(machines_est.items(), key=lambda x: x[1]["LA_EFT"]))
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
