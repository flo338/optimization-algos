"""Defines a protocol for neighborhoods."""

from abc import abstractmethod
from typing import Literal, Protocol

from app.optimization.solution import ProblemSolution


class Neighborhood(Protocol):
    """Defines the protocol for a neighborhood."""

    @abstractmethod
    def get_neighbors(
        self,
        solution: ProblemSolution,
        method: Literal["exhaustive", "stochastic"] = "stochastic",
    ) -> list[ProblemSolution]:
        """return neighbors given a certain method."""
        match method:
            case "exhaustive":
                return self._get_neighbors_exhaustive(solution=solution)
            case "stochastic":
                return self._get_neighbors_stochastic(solution=solution)
            case _:
                raise ValueError(f"method: {method} not available")

    @abstractmethod
    def _get_neighbors_exhaustive(
        self, solution: ProblemSolution
    ) -> list[ProblemSolution]:
        """Must be implemented for exhaustive neighbor generation"""
        raise NotImplementedError

    @abstractmethod
    def _get_neighbors_stochastic(
        self, solution: ProblemSolution
    ) -> list[ProblemSolution]:
        """Must be implemented for meta heuristics needing stochastic neighbor generation as eg simulated annealing."""
        raise NotImplementedError
