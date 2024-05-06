from collections import OrderedDict, defaultdict, deque

from optimization.heuristic.base import Heuristic


class PEFT(Heuristic):
    def __init__(self, w, dataset_machines, succ, pred, data):
        super().__init__(w, dataset_machines, succ, pred, data)
        self.name = "PEFT"

    def OCT(self, task, task_machine, machines, c_i_j_line, memo):
        if memo.get(task) and memo.get(task).get(task_machine):
            return memo[task][task_machine]

        if not self.succ[task]:
            memo[task][task_machine] = 0
            return memo[task][task_machine]

        to_see = []
        for suc in self.succ[task]:
            find_min = []
            for machine_name, machine_data in machines.items():
                v = self.OCT(suc, machine_name, machines, c_i_j_line, memo)

                c_i_j = 0
                if machine_name != task_machine:
                    c_i_j = c_i_j_line[task][suc]
                val = v + c_i_j + self.w[machine_data.data["name"]][suc]
                find_min.append(val)

            to_see.append(min(find_min))

        memo[task][task_machine] = max(to_see)
        return memo[task][task_machine]

    def generate_rank(self, B_m_n, B_m_n_line, w_line, machines):
        L_m, L_line = self.generate_L(len(machines))
        c_proc_i_j, c_i_j_line = self.generate_C(machines, L_line, B_m_n, B_m_n_line)

        oct_table = defaultdict(dict)
        rank_oct = {}
        P = len(machines)

        q = deque([self.last])
        while q:
            current = q.popleft()
            for task_machine in machines:
                self.OCT(current, task_machine, machines, c_i_j_line, oct_table)

            to_add = self.pred[current]
            q.extend(to_add)

        rank_oct = {task_name: (sum([v for v in values.values()]) / P) for task_name, values in oct_table.items()}
        rank_oct["root"] = float("inf")
        rank_oct["end"] = -1
        rank_oct = OrderedDict(sorted(rank_oct.items(), key=lambda x: x[1], reverse=True))
        return rank_oct, c_proc_i_j, oct_table

    def generate_assignment(self, machines, c_proc_i_j, rank, oct_table):
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
