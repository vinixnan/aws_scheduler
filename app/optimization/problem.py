import math
from collections import defaultdict

import numpy as np
from pymoo.core.problem import ElementwiseProblem


class AWSProblemDirect(ElementwiseProblem):
    def __init__(
        self,
        n_var,
        machines_data,
        region_name,
        problem_file_path,
        elementwise_runner=None,
        heu=None,
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
        super().__init__(
            n_var=n_var,
            n_obj=2,
            n_constr=1,
            xl=xl,
            xu=xu,
            vtype=int,
            elementwise_runner=elementwise_runner,
        )

    def run_heu(self, machine_types):
        assignment, makespan, _, _, machines = self.heu.schedule(machine_types)
        clean_assignment = {k: v for k, v in assignment.items() if len(v) > 0}
        machines = {k: v for k, v in machines.items() if k in clean_assignment.keys()}
        price = math.ceil(makespan / 3600) * sum([machine.data["pricePerUnit"] for machine in machines.values()])
        return makespan, price, clean_assignment, machines

    def _evaluate(self, x, out, *args, **kwargs):
        makespan, price, clean_assignment, violations = self.calculate_fitness(x)
        out["F"] = [makespan, price]
        out["G"] = [violations]
        to_save_data = {}
        to_save_data["assignment"] = clean_assignment
        to_save_data["data"] = {"makespan": makespan, "price": price, "X": [int(el) for el in x]}
        out["saved_data"] = to_save_data

    def show_solution(self, sol):
        return [self.ids[x] for x in sol.X if x > 0]

    def calculate_fitness(self, X):
        used_machines = [self.ids[ins] for ins in X if ins > 0]
        violations = 0
        if len(used_machines) <= 1:
            violations = len(used_machines)
            return float("inf"), float("inf"), dict(), violations

        makespan, price, assignment, machines = self.run_heu(used_machines)

        i = 0
        clean_assignment = defaultdict(dict)
        for machine_id, t_list in assignment.items():
            if len(t_list) > 0:
                machine_data = machines[machine_id]
                machine_type = machine_data.data["name"]
                to_add = {}
                for t in t_list:
                    to_add[t["name"]] = {'machine_type':machine_type, 'AFT':t['AFT'], 'EST':t['EST']}

                clean_assignment[machine_id] = to_add
                X[i] = self.ids_rev[machine_type]
                i = i + 1
        while i < len(X):
            X[i] = -1
            i = i + 1

        return makespan, price, clean_assignment, 0


def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


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
