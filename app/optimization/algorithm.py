from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from optimization.problem import AWSProblem


def create_algorithm(problem):
    algorithm = NSGA2(pop_size=100,
        sampling=IntegerRandomSampling(),
        crossover=TwoPointCrossover(),
        mutation=BitflipMutation(),
        eliminate_duplicates=True
    )
    return algorithm

def run(problem):
    algorithm=create_algorithm(problem)
    return minimize(problem,
        algorithm,
        ('n_gen', 500),
        seed=1,
        verbose=False
    )

def run_all(number_of_tasks, regions, dccv):
    all_regions_pop=[]
    for region in regions:
        problem = AWSProblem(number_of_tasks, dccv, region)
        res=run(problem)
        for s in res.pop:
            s.region = region
            s.x_aws = [problem.ids[el] for el in s.X if el > 0]
        all_regions_pop.extend(res.pop)
    return all_regions_pop


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
    #fullly dominates
    return 1
  if worse == len(s1):
    #fully dominated
    return -1
  if eq == len(s1):
    #exactly the same
    return 0

  if better > 0 and worse == 0:
    #dominates a little
    return 1
  if worse > 0 and better == 0:
    #is dominated a little
    return -1
  return 0

def remove_dominated(pop):
  returning=[]
  for i in range(len(pop)):
    dominated=False
    for j in range(len(pop)):
      if i!=j:
        if dominates(pop[i], pop[j]) == -1:
          dominated=True
          break
    if not dominated:
      returning.append(pop[i])
  return returning

def invert_maximization(pop):
  for s in pop:
    F=list(s.F)
    F[1]=F[1]*-1
    s.F=F


def associate_aws_data_with_solution(PF, dccv):
  for sol in PF:
    region_machines = dccv[sol.region]
    ndv = [(name, region_machines[name]) for name in sol.x_aws]
    for name, data in ndv:
      data['flop'] = data['ecu'] * 4.4
    sol.x_aws = ndv
