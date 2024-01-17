from pymoo.algorithms.moo.sms import (
    SMSEMOA,
    cv_and_dom_tournament,
    LeastHypervolumeContributionSurvival,
)
from optimization.pysimgrid_bridge import get_pysim_data
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.util.display.multi import MultiObjectiveOutput


class ISMSEMOA(SMSEMOA):
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
            selection=TournamentSelection(func_comp=cv_and_dom_tournament),
            survival=LeastHypervolumeContributionSurvival(),
            crossover=crossover,
            mutation=mutation,
            output=MultiObjectiveOutput(),
        )

    def _infill(self):
        off = super()._infill()
        for sol in off:
            get_pysim_data(sol, [self.heuristic_name], None)
        return off
