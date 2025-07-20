from optimization.instance_base import ProblemInstance
from optimization.local_search.neighborhood import Neighborhood
from optimization.local_search.objective import Objective
from optimization.solution import ProblemSolution


class ProblemInstanceLocalSearch(ProblemInstance):
    neighborhood: Neighborhood
    objective: Objective

    def obj(self, solution: list[ProblemSolution]) -> list[float]:
        return self.objective.obj(solution=solution)
