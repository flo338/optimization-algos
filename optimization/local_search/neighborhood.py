from abc import ABC, abstractmethod
from optimization.solution import ProblemSolution


class Neighborhood(ABC):
    @abstractmethod
    def get_neighbors(
        self,
        solution: ProblemSolution,
    ) -> list[ProblemSolution]:
        raise NotImplementedError
