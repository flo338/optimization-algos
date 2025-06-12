"""Defines a protocol for an objective"""

from abc import abstractmethod
from typing import Protocol

from optimization.solution import ProblemSolution


class Objective(Protocol):
    @staticmethod
    @abstractmethod
    def obj(solution: list[ProblemSolution]) -> list[float]:
        raise NotImplementedError
