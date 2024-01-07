from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import IntegerRandomSampling


class Algorithm:
    def __init__(self, problem, region, seed=None, verbose=False):
        self.problem = problem
        self.pop_size = 100
        self.eliminate_duplicates = True
        self.algorithm = None
        self.n_gen = 500
        self.seed = seed
        self.verbose = verbose
        self.region = region

    def create_algorithm(self):
        self.algorithm = NSGA2(
            pop_size=self.pop_size,
            sampling=IntegerRandomSampling(),
            crossover=TwoPointCrossover(),
            mutation=BitflipMutation(),
            eliminate_duplicates=self.eliminate_duplicates,
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
            self.problem.x_to_aws(s)
            s.problem = self.problem
        return res


def run_all(problems, seed=None, verbose=False):
    all_regions_pop = []
    for problem in problems:
        alg = Algorithm(problem, problem.region, seed, verbose)
        res = alg.run()
        all_regions_pop.extend(res.pop)
    return all_regions_pop
