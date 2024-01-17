from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga2 import binary_tournament
from optimization.pysimgrid_bridge import get_pysim_data
from pymoo.operators.survival.rank_and_crowding import RankAndCrowding
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.util.display.multi import MultiObjectiveOutput


class INSGA2(NSGA2):
    def __init__(
        self,
        problem,
        heuristic_name,
        pop_size,
        sampling,
        crossover,
        mutation,
        eliminate_duplicates,
    ):
        self.heuristic_name = heuristic_name
        self.problem = problem
        super().__init__(
            pop_size=pop_size,
            sampling=sampling,
            selection=TournamentSelection(func_comp=binary_tournament),
            crossover=crossover,
            mutation=mutation,
            survival=RankAndCrowding(),
            output=MultiObjectiveOutput(),
            eliminate_duplicates=eliminate_duplicates,
        )

    def _advance(self, infills=None, **kwargs):
        if infills is not None:
            print(len(infills))
            for s in infills:
                s.region ="AWS"
                self.problem.x_to_aws(s)
                s.problem = self.problem
                get_pysim_data(s, [self.heuristic_name],  None)
        super()._advance(infills=infills, **kwargs)
