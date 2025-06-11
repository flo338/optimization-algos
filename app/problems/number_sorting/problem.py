"""Defines a problem instance to sort a list of numbers as a figurative example"""

import numpy as np

from optimization.local_search.instance import ProblemInstance
from optimization.local_search.neighborhood import Neighborhood
from optimization.local_search.objective import Objective
from app.optimization.solution import ProblemSolution


class NumberSortingSolution(ProblemSolution):
    def __init__(self, solution: np.ndarray):
        self.solution = solution


class NumberSortingNeighborhood(Neighborhood):
    @staticmethod
    def _one_swap_permutations(array_: np.ndarray) -> np.ndarray:
        """Produces all permutations of a list, where each time only one item pair is swapped."""
        n = array_.shape[0]
        swaps = []

        for i in range(n):
            for j in range(i + 1, n):
                swapped = array_.copy()
                swapped[i], swapped[j] = swapped[j], swapped[i]
                swaps.append(swapped)

        return np.array(swaps)

    def get_neighbors(
        self, solution: NumberSortingSolution
    ) -> list[NumberSortingSolution]:
        return [
            NumberSortingSolution(solution=sol)
            for sol in self._one_swap_permutations(solution.solution)
        ]


class NumberSortingObjectiveStochastically(Objective):
    @staticmethod
    def obj(solution: list[NumberSortingSolution]) -> list[float]:
        """determines the 'sortedness' of an array stochastically"""

        n = solution[0].solution.shape[0]
        samples = int(10000 * (1 + 1 / n))
        index_pairs = np.random.randint(0, n, 2 * samples)

        solution_arr = np.array([sol.solution for sol in solution])

        scores = np.zeros(len(solution))

        for i, j in zip(
            index_pairs[: index_pairs.shape[0] // 2],
            index_pairs[index_pairs.shape[0] // 2 :],
        ):
            if i == j:
                samples -= 1
                continue

            scores += (
                solution_arr[:, i] < solution_arr[:, j]
                if i < j
                else solution_arr[:, i] > solution_arr[:, j]
            )

        return scores / samples


class NumberSortingObjective(Objective):
    @staticmethod
    def obj(solution: list[NumberSortingSolution]) -> list[float]:
        """determines the 'sortedness' by number of local violations"""

        n = solution[0].solution.shape[0]
        violations = np.zeros(len(solution))
        solution_arr = np.array([sol.solution for sol in solution])

        for ix in range(n - 1):
            violations += solution_arr[:, ix] > solution_arr[:, ix + 1]

        return 1 - (violations / n)


class NumberSorting(ProblemInstance):
    def __init__(self):
        self.neighborhood = NumberSortingNeighborhood()
        self.objective = NumberSortingObjectiveStochastically()

    def _generate_feasible_solution(self) -> NumberSortingSolution: ...

    def is_feasible_sol(self, solution: NumberSortingSolution) -> bool:
        if len(solution.solution) > 0 and len(solution.solution.shape) == 1:
            return True
        return False
