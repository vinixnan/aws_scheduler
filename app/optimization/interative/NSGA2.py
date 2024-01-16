from pymoo.algorithms.moo.nsga2 import NSGA2
from optimization.generate import get_pysim_data


class INSGA2(NSGA2):
    def __init__(
        self,
        heuristic_name,
        pop_size,
        sampling,
        selection,
        crossover,
        mutation,
        survival,
        output,
    ):
        self.heuristic_name = heuristic_name
        super().__init__(
            pop_size=pop_size,
            sampling=sampling,
            selection=selection,
            crossover=crossover,
            mutation=mutation,
            survival=survival,
            output=output,
        )

    def _infill(self):
        off = super()._infill()
        for sol in off:
            get_pysim_data(sol, [self.heuristic_name], None)
        return off
