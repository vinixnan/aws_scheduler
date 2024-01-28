from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.age import AGEMOEA
from pymoo.algorithms.moo.sms import SMSEMOA
from pymoo.optimize import minimize
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import IntegerRandomSampling


class Algorithm:
    def __init__(
        self, algorithm_name, n_gen, pop_size, problem, region, seed=None, verbose=False
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

    def create_algorithm(self):
        sampling = IntegerRandomSampling()
        crossover = TwoPointCrossover(prob=0.9)
        # mutation_probability = 1.0 / self.problem.n_var
        mutation_probability = 0.1
        mutation = BitflipMutation(prob=mutation_probability)
        if "NSGA" in self.algorithm_name:
            self.algorithm = NSGA2(
                pop_size=self.pop_size,
                sampling=sampling,
                crossover=crossover,
                mutation=mutation,
                eliminate_duplicates=self.eliminate_duplicates,
            )
        elif self.algorithm_name == "AGEMOEA":
            self.algorithm = AGEMOEA(
                pop_size=self.pop_size,
                sampling=sampling,
                crossover=crossover,
                mutation=mutation,
                eliminate_duplicates=self.eliminate_duplicates,
            )
        elif self.algorithm_name == "SMSEMOA":
            self.algorithm = SMSEMOA(
                pop_size=self.pop_size,
                sampling=sampling,
                crossover=crossover,
                mutation=mutation,
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
