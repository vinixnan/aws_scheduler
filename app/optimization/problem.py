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