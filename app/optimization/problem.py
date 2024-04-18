import numpy as np
from pymoo.core.problem import ElementwiseProblem
from yattag import Doc, indent
import math


class Instance:
    def __init__(self, id, instance_type, data):
        self.name = "host" + str(id)
        self.link = "link" + str(id)
        self.instance_type = instance_type
        self.active = True
        self.data = data


class AWSProblem(ElementwiseProblem):
    def __init__(self, n_var, dccv, region, problem_file_path):
        self.region = region
        self.base = dccv[self.region]
        enumerated = enumerate(self.base.keys(), 1)
        self.ids = {k: v for k, v in enumerated}
        self.ids_rev = {v: k for k, v in self.ids.items()}
        self.problem_file_path = problem_file_path
        self.smaller_machine = min(self.base.values(), key=lambda x: x["pricePerUnit"])
        xl = np.zeros(n_var)
        xu = np.ones(n_var) * max(self.ids.keys())
        super().__init__(n_var=n_var, n_obj=2, n_constr=2, xl=xl, xu=xu, vtype=int)

    def _evaluate(self, x, out, *args, **kwargs):
        total, power, violations = self.calculate_fitness(x)
        out["F"] = [total, power]
        out["G"] = [violations, violations]

    def calculate_fitness(self, X):
        sub_dict = [self.base[self.ids[ins]] for ins in X if ins > 0]
        total = sum([v["pricePerUnit"] for v in sub_dict])
        power = sum([v["ecu"] for v in sub_dict]) * -1
        violations = 0
        if len(sub_dict) == 0:
            violations = 1
        return total, power, violations

    def x_to_aws(self, s):
        s.x_aws = [self.ids[el] for el in s.X if el > 0]

    def aws_to_x(self, s):
        x = [self.ids_rev[name] for name in s.x_aws]
        s.X = np.array(x)

    def generate_simgrid_xml(self, machines):
        doc, tag, _ = Doc().tagtext()
        doc.asis("<?xml version='1.0'?>")
        doc.asis('<!DOCTYPE platform SYSTEM "http://simgrid.gforge.inria.fr/simgrid/simgrid.dtd">')

        with tag("platform", version="4"):
            with tag("AS", id="AS0", routing="Floyd"):
                for machine in machines.values():
                    doc.stag(
                        "host",
                        id=machine.name,
                        core=machine.data["vcpu"],
                        speed=machine.data["flop"],
                    )
                    doc.stag(
                        "link",
                        id=machine.link,
                        bandwidth=str(machine.data["networkPerformance"]) + "Bps",
                        latency="0.0001s",
                    )
                keys = list(machines.keys())
                origin = machines[keys[0]]
                for j in range(1, len(keys)):
                    destiny = machines[keys[j]]
                    with tag("route", src=origin.name, dst=destiny.name):
                        doc.stag("link_ctn", id=origin.link)

        return indent(doc.getvalue(), indentation=" " * 4, newline="\r\n")

    def update_decision_variables(self, sol, makespan):
        self.aws_to_x(sol)
        total, _, _ = self.calculate_fitness(sol.X)
        # seconds to hours
        sol.F[0] = makespan
        sol.F[1] = total * math.ceil(makespan / 3600)


def dominates(s1s, s2s):
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


def remove_dominated(pop):
    returning = []
    for i in range(len(pop)):
        dominated = False
        for j in range(len(pop)):
            if i != j:
                if dominates(pop[i], pop[j]) == -1:
                    dominated = True
                    break
        if not dominated:
            returning.append(pop[i])
    return returning


def invert_maximization(pop):
    for s in pop:
        F = list(s.F)
        F[1] = F[1] * -1
        s.F = F


def get_problems(number_of_tasks, regions, dccv, problem_file_path):
    problems = []
    for region in regions:
        problem = AWSProblem(number_of_tasks, dccv, region, problem_file_path)
        problems.append(problem)
    return problems
