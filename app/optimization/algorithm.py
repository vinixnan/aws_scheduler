from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.age import AGEMOEA
from pymoo.algorithms.moo.sms import SMSEMOA
from pymoo.optimize import minimize
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from interative.NSGA2 import INSGA2
from interative.AGEMOEA import IAGEMOEA
from interative.SMSEMOA import ISMSEMOA


class Algorithm:
    def __init__(
        self,
        algorithm_name,
        n_gen,
        pop_size,
        problem,
        region,
        seed=None,
        verbose=False,
        interative=False,
    ):
        self.problem = problem
        self.pop_size = pop_size
        self.eliminate_duplicates = True
        self.algorithm = None
        self.algorithm_name = algorithm_name.upper()
        self.n_gen = n_gen
        self.seed = seed
        self.verbose = verbose
        self.region = region
        self.interative = interative

    def create_algorithm(self):
        if "NSGA" in self.algorithm_name:
            self.algorithm = NSGA2(
                pop_size=self.pop_size,
                sampling=IntegerRandomSampling(),
                crossover=TwoPointCrossover(),
                mutation=BitflipMutation(),
                eliminate_duplicates=self.eliminate_duplicates,
            )
        elif self.algorithm_name == "AGEMOEA":
            self.algorithm = AGEMOEA(
                pop_size=self.pop_size,
                sampling=IntegerRandomSampling(),
                crossover=TwoPointCrossover(),
                mutation=BitflipMutation(),
                eliminate_duplicates=self.eliminate_duplicates,
            )
        elif self.algorithm_name == "SMSEMOA":
            self.algorithm = SMSEMOA(
                pop_size=self.pop_size,
                sampling=IntegerRandomSampling(),
                crossover=TwoPointCrossover(),
                mutation=BitflipMutation(),
                eliminate_duplicates=self.eliminate_duplicates,
            )

    def create_I_algorithm(self, heuristic_name):
        if "NSGA" in self.algorithm_name:
            self.algorithm = INSGA2(
                heuristic_name,
                pop_size=self.pop_size,
                sampling=IntegerRandomSampling(),
                crossover=TwoPointCrossover(),
                mutation=BitflipMutation(),
                eliminate_duplicates=self.eliminate_duplicates,
            )
        elif self.algorithm_name == "AGEMOEA":
            self.algorithm = IAGEMOEA(
                heuristic_name,
                pop_size=self.pop_size,
                sampling=IntegerRandomSampling(),
                crossover=TwoPointCrossover(),
                mutation=BitflipMutation(),
                eliminate_duplicates=self.eliminate_duplicates,
            )
        elif self.algorithm_name == "SMSEMOA":
            self.algorithm = ISMSEMOA(
                heuristic_name,
                pop_size=self.pop_size,
                sampling=IntegerRandomSampling(),
                crossover=TwoPointCrossover(),
                mutation=BitflipMutation(),
                eliminate_duplicates=self.eliminate_duplicates,
            )

    def run(self, heuristic_name=None):
        if not self.interative:
            self.create_algorithm()
        else:
            self.create_I_algorithm(heuristic_name)
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
            config.interative,
        )
        res = alg.run(config.heuristic_name)
        all_regions_pop.extend(res.pop)
    return all_regions_pop
