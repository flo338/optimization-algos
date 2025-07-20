from abc import ABC, abstractmethod

from optimization.solution import ProblemSolution


class Objective(ABC):
    @abstractmethod
    def obj(self, solution: list[ProblemSolution]) -> list[float]:
        raise NotImplementedError
