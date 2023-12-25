import numpy as np
from pymoo.core.problem import ElementwiseProblem

class AWSProblem(ElementwiseProblem):
    def __init__(self, n_var, dccv, region):
        self.region = region
        self.base = dccv[self.region]
        self.ids = {k:v for k,v in enumerate(self.base.keys(), 1)}
        self.ids[0] = None

        xl = np.zeros(n_var)
        xu = np.ones(n_var) * max(self.ids.keys())
        super().__init__(n_var=n_var, n_obj=2, n_constr=2, xl=xl, xu=xu, vtype=int)

    def _evaluate(self, x, out, *args, **kwargs):
          sub_dict = {self.ids[ins]:self.base[self.ids[ins]] for ins in x if ins > 0}
          total = sum([v['pricePerUnit'] for v in sub_dict.values()])
          power = sum([v['ecu'] for v in sub_dict.values()]) * -1
          out["F"] = [total, power]
          violations = 0
          if len(sub_dict) == 0:
            violations = 1
          out["G"] = [violations, violations]



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

