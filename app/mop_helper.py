from pymoo.core.problem import ElementwiseProblem
import numpy as np
import math
from pysim_helper import Machine, get_pysim_data


def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


class AWSProblemDirect(ElementwiseProblem):
    def __init__(
        self,
        n_var,
        machines_data,
        region_name,
        problem_file_path,
        elementwise_runner=None,
        heu="HEFT",
    ):
        self.region_name = region_name
        self.heu = heu
        self.machines_data = machines_data
        self.problem_file_path = problem_file_path
        self.ids = {k: v for k, v in enumerate(self.machines_data.keys(), 1)}
        self.ids_rev = {v: k for k, v in self.ids.items()}
        print(region_name, self.ids)
        xl = np.zeros(n_var)
        xu = np.ones(n_var) * max(self.ids.keys())
        self.ccc = 0
        super().__init__(
            n_var=n_var,
            n_obj=2,
            n_constr=1,
            xl=xl,
            xu=xu,
            vtype=int,
            elementwise_runner=elementwise_runner,
        )

    def pysim(self, selected_region_machines, heu):
        machines = {}
        for i, machine_data in enumerate(selected_region_machines):
            mach = Machine("host" + str(i), machine_data, "link" + str(i))
            machines[mach.name] = mach

        resp = get_pysim_data(machines, self.problem_file_path, heu)
        machines = {k: v for k, v in machines.items() if k in resp["tasks"].keys()}
        price = math.ceil(float(resp["makespan"]) / 3600) * sum(
            [machine.data["pricePerUnit"] for machine in machines.values()]
        )
        return resp["makespan"], price, resp["tasks"]

    def _evaluate(self, x, out, *args, **kwargs):
        makespan, price, tasks, violations = self.calculate_fitness(x)
        out["F"] = [makespan, price]
        out["G"] = [violations]

    def show_solution(self, sol):
        return [self.ids[x] for x in sol.X if x > 0]

    def calculate_fitness(self, X):
        used_machines = [self.machines_data[self.ids[ins]] for ins in X if ins > 0]
        violations = 0
        if len(used_machines) <= 1:
            violations = len(used_machines)
            return float("inf"), float("inf"), None, violations

        makespan, price, tasks = self.pysim(used_machines, self.heu)
        data = {}
        data["makespan"] = makespan
        data["price"] = price
        data["tasks"] = tasks

        self.ccc = self.ccc + 1
        return data["makespan"], data["price"], data["tasks"], 0


class AWSProblem(ElementwiseProblem):
    def __init__(self, n_var, machines_data, region_name):
        self.region_name = region_name
        self.machines_data = machines_data
        self.ids = {k: v for k, v in enumerate(self.machines_data.keys(), 1)}
        self.ids_rev = {v: k for k, v in self.ids.items()}
        print(region_name, self.ids)
        xl = np.zeros(n_var)
        xu = np.ones(n_var) * max(self.ids.keys())
        print(n_var)
        super().__init__(n_var=n_var, n_obj=2, n_constr=1, xl=xl, xu=xu, vtype=int)

    def _evaluate(self, x, out, *args, **kwargs):
        ecu, price_per_ecu, network_performance, violations = self.calculate_fitness(x)
        out["F"] = [ecu, network_performance]
        out["G"] = [violations]

    def show_solution(self, sol):
        return [self.ids[x] for x in sol.X if x > 0]

    def calculate_fitness(self, X):
        used_machines = [self.machines_data[self.ids[ins]] for ins in X if ins > 0]
        violations = 0
        if len(used_machines) == 0:
            violations = 2
        elif len(used_machines) == 1:
            violations = 1

        network_performance = sum([v["pricePerUnit"] for v in used_machines])
        price_per_ecu = sum([v["price_per_ecu"] for v in used_machines])
        ecu = sum([v["ecu"] for v in used_machines]) * -1
        return ecu, price_per_ecu, network_performance, violations


def dominates_sol(s1s, s2s):
    s1 = s1s.F
    s2 = s2s.F
    better = 0
    eq = 0
    worse = 0
    for i in range(len(s1)):
        if s1[i] < s2[i]:
            better = better + 1
        elif s1[i] == s2[i]:
            eq = eq + 1
        else:
            worse = worse + 1

    if better == len(s1):
        # fullly dominates
        return 1
    if worse == len(s1):
        # fully dominated
        return -1
    if eq == len(s1):
        # exactly the same
        return 0

    if better > 0 and worse == 0:
        # dominates a little
        return 1
    if worse > 0 and better == 0:
        # is dominated a little
        return -1
    return 0


def remove_dominated_sol(pop):
    returning = []
    for i in range(len(pop)):
        dominated = False
        for j in range(len(pop)):
            if i != j:
                if dominates_sol(pop[i], pop[j]) == -1:
                    dominated = True
                    break
        if not dominated:
            returning.append(pop[i])
    return returning
