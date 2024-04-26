import os
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict

from optimization.pysimgrid.pysim_helper import get_pysim_data
from utils.definitions import Machine
from utils.files import read_yaml, save_yaml


class Heuristic(ABC):
    def __init__(self, w, dataset_machines, succ, pred, data):
        self.dataset_machines = dataset_machines
        self.w = w
        self.pred = pred
        self.succ = OrderedDict(sorted(succ.items(), key=lambda x: len(x[1])))
        self.data = data
        self.task_names = list(succ.keys())
        self.last = "end"
        self.name = None

    def schedule(self, machine_types):
        machines = {}
        for i, machine_data in enumerate(machine_types):
            mach = Machine("host" + str(i), self.dataset_machines[machine_data], "link" + str(i))
            machines[mach.name] = mach
        B_m_n, B_m_n_line = self.generate_B(machine_types, machines)
        assignment, makespan, first_host, last_host = self.schedule_with_data(
            machine_types, machines, B_m_n_line, B_m_n
        )
        return assignment, makespan, first_host, last_host, machines

    def schedule_with_data(self, machine_types, machines, B_m_n_line, B_m_n):
        w_line = self.generate_W_line(machine_types)
        rank, c_proc_i_j, table = self.generate_rank(B_m_n, B_m_n_line, w_line, machines)
        return self.generate_assignment(machines, c_proc_i_j, rank, table)

    @abstractmethod
    def generate_assignment(self, machines, c_proc_i_j, rank, table=None):
        pass

    @abstractmethod
    def generate_rank(self, B_m_n, B_m_n_line, w_line, machines):
        pass

    def calc_EST(self, task, task_machine, assignment, c_proc_i_j, makespans, memo):
        if memo.get(task):
            return memo[task]

        values = []
        for t in self.pred.get(task, []):
            data = self.calc_EST(t, task_machine, assignment, c_proc_i_j, makespans, memo)
            cj = c_proc_i_j[t][task][data["machine"]][task_machine]
            val = data["AFT"] + cj
            values.append(val)

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

    def generate_C(self, machines, L_line, B_m_n, B_m_n_line):
        c_proc_i_j = {}
        for task_i in self.task_names:
            for machine_type_i in machines.keys():
                for task_j in self.task_names:
                    if task_i != task_j:
                        for machine_type_j in machines.keys():
                            task_i_dependent = self.succ.get(task_i, [])
                            if task_j in task_i_dependent:
                                value = 0
                                if machine_type_j != machine_type_i:
                                    value = (sum(L_line) / len(L_line)) + (
                                        self.data[task_i][task_j] / B_m_n[machine_type_j]
                                    )

                                if not c_proc_i_j.get(task_i):
                                    c_proc_i_j[task_i] = {}
                                if not c_proc_i_j[task_i].get(task_j):
                                    c_proc_i_j[task_i][task_j] = {}
                                if not c_proc_i_j[task_i][task_j].get(machine_type_i):
                                    c_proc_i_j[task_i][task_j][machine_type_i] = {}

                                c_proc_i_j[task_i][task_j][machine_type_i][machine_type_j] = value

        c_i_j_line = defaultdict(dict)
        for task_i in self.task_names:
            for task_j in self.task_names:
                if task_i != task_j:
                    task_i_dependent = self.succ.get(task_i, [])
                    if task_j in task_i_dependent:
                        c_i_j_line[task_i][task_j] = (sum(L_line) / len(L_line)) + (
                            self.data[task_i][task_j] / B_m_n_line
                        )

        return c_proc_i_j, c_i_j_line

    def generate_W_line(self, machine_types):
        w_line = defaultdict(dict)
        for task in self.task_names:
            all_task_size = [self.w[machine_type][task] for machine_type in machine_types]
            w_line[task] = sum(all_task_size) / len(all_task_size)
        return w_line

    def generate_B(self, machine_types, machines):
        all_networks = [(self.dataset_machines[machine_type]["networkPerformance"]) for machine_type in machine_types]
        B_m_n_line = sum(all_networks) / len(all_networks)
        B_m_n = {
            machine_name: (machine_data.data["networkPerformance"]) for machine_name, machine_data in machines.items()
        }
        return B_m_n, B_m_n_line

    def generate_L(self, qtd_machine):
        L_m = 0.00000001 * 1000
        L_line = [0.00000001 * 1000] * qtd_machine
        L_m = 0
        L_line = [0] * qtd_machine
        return L_m, L_line


def generate_W(config, problem, problem_file_path, regions, region_machines_dataset):
    if config.eager_aws or not os.path.isfile("execution_time/" + problem + "_machine_execution_time.yml"):
        dc_region_machines_task_time = {}
        for region in regions:
            dataset_machines = region_machines_dataset[region]
            dc_machines_task_time = {}
            for machine_name, machine_data in dataset_machines.items():
                selected_region_machines = [machine_data] * 2
                machines = {}
                for i, machine_data in enumerate(selected_region_machines):
                    mach = Machine("host" + str(i), machine_data, "link" + str(i))
                    machines[mach.name] = mach

                resp = get_pysim_data(machines, problem_file_path, "HEFT", False)
                tasks = {}
                for host_tasks in resp["tasks"].values():
                    for task in host_tasks:
                        tasks[task["name"]] = task["finish_time"] - task["start_time"]

                dc_machines_task_time[machine_name] = tasks

            dc_region_machines_task_time[region] = dc_machines_task_time

        save_yaml(dc_region_machines_task_time, "execution_time/" + problem + "_machine_execution_time.yml")

    else:
        dc_region_machines_task_time = read_yaml("execution_time/" + problem + "_machine_execution_time.yml")

    for region in regions:
        dc_machines_task_time = dc_region_machines_task_time[region]
        for machine_name, tasks in dc_machines_task_time.items():
            tasks["root"] = 0
            tasks["end"] = 0

    return dc_region_machines_task_time
