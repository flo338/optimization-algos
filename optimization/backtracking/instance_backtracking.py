from abc import abstractmethod
from typing import Any
from optimization.instance_base import ProblemInstance
from optimization.solution import ProblemSolution


class ProblemInstanceBacktracking(ProblemInstance):
    @abstractmethod
    def is_feasible_value(self, val: Any, var: Any, solution: ProblemSolution) -> bool:
        """
        Checks if value is feasible for variable.
        """
        raise NotImplementedError

    @abstractmethod
    def assign_value(
        self, val: Any, var: Any, solution: ProblemSolution
    ) -> ProblemSolution:
        """
        Assigns a value to a variable and returns new partial solution
        """
        raise NotImplementedError

    @abstractmethod
    def get_values(
        self, var: Any, solution: ProblemSolution, pruned_vals: set[Any]
    ) -> list[Any]:
        """
        Returns all values for a variable. Optionally can already prune some values.
        """
        raise NotImplementedError

    @abstractmethod
    def choose_variable(self, vars: set[Any], solution: ProblemSolution) -> Any:
        """
        Chooses the next variable. Variable must be hashable.
        """
        raise NotImplementedError
