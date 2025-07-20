from abc import ABC, abstractmethod

from optimization.exceptions import ErrorWhileGeneratingSolution
from optimization.solution import ProblemSolution


class ProblemInstance(ABC):
    @abstractmethod
    def _generate_feasible_solution(self) -> ProblemSolution:
        raise NotImplementedError

    def generate_feasible_solution(self) -> ProblemSolution:
        try:
            return self._generate_feasible_solution()
        except ErrorWhileGeneratingSolution as e:
            raise ErrorWhileGeneratingSolution("Can't find feasible solution") from e

    @abstractmethod
    def is_feasible_sol(self, solution: ProblemSolution) -> bool:
        raise NotImplementedError()


class InstanceFactory(ABC):
    @abstractmethod
    def generate_instance() -> ProblemInstance:
        raise NotImplementedError()
