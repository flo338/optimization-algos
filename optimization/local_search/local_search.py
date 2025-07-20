from abc import ABC, abstractmethod

import numpy as np

from optimization.exceptions import (
    ErrorDuringStep,
    ErrorNoImprovement,
    ErrorStepLimit,
)
from optimization.local_search.instance_local_search import ProblemInstanceLocalSearch
from optimization.solution import ProblemSolution


class LocalSearch(ABC):
    """
    A protocol for local search algorithms. The local search class takes a problem instance,
    and an amount of steps.
    """

    _instance: ProblemInstanceLocalSearch
    _steps: int
    _curr_step: int = 0
    _tries: int = 0
    _attempts: int

    def __init__(
        self,
        instance: ProblemInstanceLocalSearch,
        steps: int,
        attempts: int = 100,
    ) -> None:
        self._instance = instance
        self._steps = steps
        self._attempts = attempts

    @abstractmethod
    def _choose(self, obj_diffs: np.ndarray) -> list[int]:
        """Logic how a neighbor is chosen."""
        raise NotImplementedError

    def _choose_neighbor(self, obj_diffs: np.ndarray) -> list[int]:
        """Method to choose a neighbor"""

        cand_neighbors = self._choose(obj_diffs=obj_diffs)

        return self._acceptance_test(solutions=cand_neighbors)

    def _acceptance_test(self, solutions: list[int]) -> list[int]:
        """Checks if a neighbor was chosen otherwise try counter is incremented."""

        if not solutions:
            # increase try counter
            self._tries += 1
            if self._tries >= self._attempts:
                raise ErrorNoImprovement("Not Improving anymore")
            return solutions

        # reset try counter
        self._tries = 0

        return solutions

    def get_current_info(self, curr_obj: float) -> str:
        raise NotImplementedError

    def search(self, start_sol: ProblemSolution | None = None) -> ProblemSolution:
        s = (
            start_sol
            if start_sol and self._instance.is_feasible_sol(start_sol)
            else self._instance.generate_feasible_solution()
        )

        for step in range(self._curr_step, self._steps):
            if s is None:
                raise ErrorDuringStep("LocalSearch.step(...) returned None")
            try:
                s = self.step(curr_sol=s)
            except ErrorNoImprovement:
                return s

        return s

    def step(self, curr_sol: ProblemSolution) -> ProblemSolution:
        """Performs one step of the local search heuristic"""

        if self._curr_step >= self._steps:
            raise ErrorStepLimit(
                f"Step limit of {self._steps} already reached. (current steps: {self._curr_step})"
            )
        self._curr_step += 1
        best_neighbor = None

        while not best_neighbor:
            neighbors = self._instance.neighborhood.get_neighbors(solution=curr_sol)

            if len(neighbors) == 0:
                self._tries += 1
                if self._tries > self._attempts:
                    raise ErrorNoImprovement("Not Improving anymore!")
                return curr_sol

            objs = self._instance.obj(neighbors)
            curr_obj = self._instance.obj([curr_sol])[0]

            obj_diffs: np.ndarray = np.array(objs) - curr_obj

            best_neighbor = self._choose_neighbor(obj_diffs=obj_diffs)

        curr_sol = neighbors[best_neighbor[0]]

        return curr_sol
