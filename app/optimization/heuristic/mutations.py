import random

import numpy as np
from pymoo.core.mutation import Mutation


class ChoiceRandomMutation(Mutation):
    def _do(self, problem, X, **kwargs):
        prob_var = self.get_prob_var(problem, size=(len(X), 1))
        Xp = np.copy(X)
        flip = np.random.random(X.shape) < prob_var
        l = list(problem.ids.keys())
        Xp[flip] = random.choice(l) * random.getrandbits(1)
        return Xp
