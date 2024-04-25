import warnings

warnings.filterwarnings("ignore", message=".*The 'nopython' keyword.*")


import numpy as np
from optimization.heuristic.mutations import ChoiceRandomMutation
from pymoo.algorithms.moo.age2 import AGEMOEA2
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.sms import SMSEMOA
from pymoo.core.evaluator import Evaluator
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.optimize import minimize


class Algorithm:
    def __init__(self, algorithm_name, n_gen, pop_size, problem, region, seed=None, verbose=False):
        self.problem = problem
        self.pop_size = pop_size
        self.eliminate_duplicates = True
        self.algorithm = None
        self.algorithm_name = algorithm_name.upper()
        self.n_gen = n_gen
        self.seed = seed
        self.verbose = verbose
        self.region = region

    def create_algorithm(self):
        sampling = IntegerRandomSampling()
        crossover = TwoPointCrossover(prob=0.9)
        mutation_probability = 0.1
        mutation = ChoiceRandomMutation(prob=mutation_probability)
        evaluator = Evaluator(callback=evaluator_callback)
        if "NSGA" in self.algorithm_name:
            self.algorithm = NSGA2(
                pop_size=self.pop_size,
                sampling=sampling,
                crossover=crossover,
                mutation=mutation,
                eliminate_duplicates=self.eliminate_duplicates,
                evaluator=evaluator,
            )

        elif self.algorithm_name == "AGEMOEA":
            self.algorithm = AGEMOEA2(
                pop_size=self.pop_size,
                sampling=sampling,
                crossover=crossover,
                mutation=mutation,
                eliminate_duplicates=self.eliminate_duplicates,
                evaluator=evaluator,
            )
        elif self.algorithm_name == "SMSEMOA":
            self.algorithm = SMSEMOA(
                pop_size=self.pop_size,
                sampling=sampling,
                crossover=crossover,
                mutation=mutation,
                eliminate_duplicates=self.eliminate_duplicates,
                evaluator=evaluator,
            )

    def run(self):
        self.create_algorithm()
        res = minimize(
            self.problem,
            self.algorithm,
            ("n_gen", self.n_gen),
            seed=self.seed,
            verbose=self.verbose,
        )
        for s in res.pop:
            s.region = self.region
        return res


def run_all(problems, config):
    all_regions_pop = []
    for problem in problems:
        alg = Algorithm(
            config.algorithm_name,
            config.n_gen,
            config.pop_size,
            problem,
            problem.region,
            config.seed,
            config.verbose,
        )
        res = alg.run()
        all_regions_pop.extend(res.pop)
    return all_regions_pop


def evaluator_callback(pop):
    for sol in pop:
        sol.X = np.array(sol.data["saved_data"].item()["data"]["X"])
