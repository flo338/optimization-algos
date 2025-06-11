"""Defines a protocol for an instance of a local search problem"""

from abc import abstractmethod
from typing import Any, Protocol

from app.optimization.local_search.neighborhood import Neighborhood
from app.optimization.local_search.objective import Objective
from app.optimization.solution import ProblemSolution


class ErrorWhileGeneratingSolution(Exception): ...


class ProblemInstance(Protocol):
    neighborhood: Neighborhood
    objective: Objective

    def generate_feasible_solution(self) -> ProblemSolution:
        """Generates a random feasible solution"""
        try:
            return self._generate_feasible_solution()
        except ErrorWhileGeneratingSolution as e:
            raise ErrorWhileGeneratingSolution("Can't find feasible solution") from e

    @abstractmethod
    def _generate_feasible_solution(self) -> ProblemSolution:
        """
        Must be implemented for local search.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def is_feasible_sol(solution: ProblemSolution) -> bool:
        """
        Must be implemented for local search.

        Validates if a solution is feasible
        """
        raise NotImplementedError()

    def obj(self, solution: list[ProblemSolution]) -> list[float]:
        return self.objective.obj(solution=solution)

    @abstractmethod
    def is_feasible_value(self, val: Any, var: Any, solution: ProblemSolution) -> bool:
        """
        Must be implemented for backtracking.
        Checks if value is feasible for variable.
        """
        raise NotImplementedError

    @abstractmethod
    def assign_value(
        self, val: Any, var: Any, solution: ProblemSolution
    ) -> ProblemSolution:
        """
        Must be implemented for backtracking.
        Assigns a value to a variable and returns new partial solution
        """
        raise NotImplementedError

    @abstractmethod
    def get_values(
        self, var: Any, solution: ProblemSolution, pruned_vals: set[Any]
    ) -> list[Any]:
        """
        Must be implemented for backtracking.
        Returns all values for a variable. Optionally can already prune some values.
        """
        raise NotImplementedError

    @abstractmethod
    def choose_variable(self, vars: set[Any], solution: ProblemSolution) -> Any:
        """
        Must be implemented for backtracking.
        Chooses the next variable. Variable must be hashable.
        """
        raise NotImplementedError


class InstanceFactory(Protocol):
    @abstractmethod
    def generate_instance() -> ProblemInstance:
        raise NotImplementedError()
