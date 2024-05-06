from collections import OrderedDict, defaultdict

from optimization.heuristic.base import Heuristic


class HEFT(Heuristic):
    def __init__(self, w, dataset_machines, succ, pred, data):
        super().__init__(w, dataset_machines, succ, pred, data)
        self.name = "HEFT"

    def recursive_transverse(self, task, c_i_j_line, w_line, memo):
        if memo.get(task):
            return memo[task]

        if not self.succ[task]:
            memo[task] = w_line[task]
            return memo[task]

        to_see = []
        for suc in self.succ[task]:
            val = self.recursive_transverse(suc, c_i_j_line, w_line, memo) + c_i_j_line[task][suc]
            to_see.append(val)

        memo[task] = max(to_see) + w_line[task]
        return memo[task]

    def generate_rank(
        self,
        B_m_n,
        B_m_n_line,
        w_line,
        machines,
    ):
        L_m, L_line = self.generate_L(len(machines))
        c_proc_i_j, c_i_j_line = self.generate_C(machines, L_line, B_m_n, B_m_n_line)
        rank_d = {}
        for task in self.succ.keys():
            self.recursive_transverse(task, c_i_j_line, w_line, rank_d)

        rank_d["root"] = float("inf")
        rank_d["end"] = -1
        rank_d = OrderedDict(sorted(rank_d.items(), key=lambda x: x[1], reverse=True))
        return rank_d, c_proc_i_j, None

    def generate_assignment(self, machines, c_proc_i_j, rank, table=None):
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
