from pymoo.algorithms.moo.age import AGEMOEA
from pymoo.algorithms.moo.nsga2 import binary_tournament
from optimization.pysimgrid_bridge import get_pysim_data
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.util.display.multi import MultiObjectiveOutput


class IAGEMOEA(AGEMOEA):
    def __init__(
        self,
        heuristic_name,
        pop_size,
        sampling,
        crossover,
        mutation,
        eliminate_duplicates,
    ):
        self.heuristic_name = heuristic_name
        super().__init__(
            pop_size=pop_size,
            sampling=sampling,
            selection=TournamentSelection(func_comp=binary_tournament),
            crossover=crossover,
            mutation=mutation,
            output=MultiObjectiveOutput(),
        )

    def _infill(self):
        off = super()._infill()
        for sol in off:
            get_pysim_data(sol, [self.heuristic_name], None)
        return off
