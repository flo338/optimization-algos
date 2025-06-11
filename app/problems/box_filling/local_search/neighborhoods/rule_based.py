from typing import Any, Literal
import numpy as np
from app.optimization.local_search.instance import ProblemInstance
from app.optimization.local_search.neighborhood import Neighborhood
from app.optimization.local_search.objective import Objective
from app.optimization.solution import ProblemSolution

POWER = 2

# Rectangle
# int x int x int
# height x width x number


def approx_needed_boxes(permutation: np.ndarray, box_size: int) -> int:
    needed_boxes = 1
    box, x = 0, 0

    for rect in permutation:
        rect_w = rect[1]

        if x + rect_w > box_size:
            box += 1  # Move to next box
            x = 0  # Reset x position

        needed_boxes += 1

        x += rect_w  # Move x forward

    return needed_boxes


def place_permutation_row_first(
    permutation: np.ndarray, box_size: int, return_idx: bool = False
) -> np.ndarray | tuple[np.ndarray, list]:
    needed_boxes = approx_needed_boxes(permutation, box_size)
    boxes = np.zeros((needed_boxes, box_size, box_size))  #
    ix = 0
    box_idx = []

    box, max_y, y, x = 0, 0, 0, 0

    for rect in permutation:
        ix += 1

        rect_h, rect_w, rect_id = rect[0], rect[1], rect[2]

        if x + rect_w > box_size:
            y += max_y
            x = 0
            max_y = 0

        if y + rect_h > box_size:
            box += 1
            box_idx.append(ix)
            y, x, max_y = 0, 0, 0

        boxes[box, int(y) : int(y + rect_h), int(x) : int(x + rect_w)] = rect_id

        x += rect_w
        max_y = max(max_y, rect_h)

    if return_idx:
        return boxes, box_idx
    return boxes


class BoxFillingSolutionRuleBased(ProblemSolution):
    def __init__(self, rectangle_permutation: np.ndarray, box_size: int) -> None:
        self.solution: np.ndarray = rectangle_permutation
        self.box_size: int = box_size


class BoxFillingObjectiveRuleBased(Objective):
    def obj(self, solution: list[BoxFillingSolutionRuleBased]) -> np.ndarray:
        neighbors = [s.solution for s in solution]
        box_size = solution[0].box_size
        needed_boxes = approx_needed_boxes(neighbors[0], box_size)

        results = np.ndarray(len(solution))
        for idx in range(len(solution)):
            realised = place_permutation_row_first(neighbors[idx], box_size=box_size)

            occ_space = np.array(
                [len(np.nonzero(row)[0]) for row in realised.reshape(needed_boxes, -1)]
            )

            results[idx] = np.sum(occ_space ** np.linspace(2, 1.1, occ_space.shape[0]))

        return results


class RuleBasedNeighborhood(Neighborhood):
    sol: BoxFillingSolutionRuleBased = BoxFillingSolutionRuleBased(np.ndarray(1), 1)

    def get_neighbors(
        self,
        solution: BoxFillingSolutionRuleBased,
        method: Literal["exhaustive"] | Literal["stochastic"] = "exhaustive",
    ) -> list[BoxFillingSolutionRuleBased]:
        return self._get_neighbors_exhaustive(solution)

    def _get_neighbors_stochastic(
        self, solution: ProblemSolution
    ) -> list[BoxFillingSolutionRuleBased]:
        return []

    def extract_and_prepend(self, lst, start, end):
        extracted = lst[start:end]  # Get the slice
        remaining = np.vstack(
            (lst[:start], lst[end:])
        )  # Remove the slice from original list
        return np.vstack((extracted, remaining))

    def _neighbor_generator(self, solution: BoxFillingSolutionRuleBased):
        neighbors = []

        _, box_idxs = place_permutation_row_first(
            solution.solution, box_size=solution.box_size, return_idx=True
        )

        for idx in range(len(box_idxs) - 1):
            start = box_idxs[idx]
            end = box_idxs[idx + 1]

            permutation = solution.solution.copy()
            yield BoxFillingSolutionRuleBased(
                self.extract_and_prepend(permutation, start, end), solution.box_size
            )

        for idx in range(0, len(solution.solution) - 1):
            for idx_neighbors in range(idx + 1, len(solution.solution)):
                permutation = solution.solution.copy()
                permutation[[idx, idx_neighbors]] = permutation[[idx_neighbors, idx]]
                yield BoxFillingSolutionRuleBased(permutation, solution.box_size)

        return neighbors

    def _get_neighbors_exhaustive(
        self, solution: BoxFillingSolutionRuleBased
    ) -> list[BoxFillingSolutionRuleBased]:
        """
        types:
            BoxFillingSolutionRuleBased.solution is a Nx3 array where each 1x3 is a representation of a rectangle.
            Each representation of a rectangle is height x width x rectangle_number.
        """

        if self.sol == solution:
            return [next(self._generator)]

        self._generator = self._neighbor_generator(solution=solution)
        self.sol = solution
        return [next(self._generator)]


class BoxFillingInstanceRuleBased(ProblemInstance):
    def __init__(
        self,
        L: int,
        rect_num: int,
        max_width: int,
        max_height: int,
        min_width: int = 1,
        min_height: int = 1,
    ) -> None:
        self.neighborhood = RuleBasedNeighborhood()
        self.objective = BoxFillingObjectiveRuleBased()

        self.L = L
        self.rect_num = rect_num
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

    def _generate_feasible_solution(self) -> BoxFillingSolutionRuleBased:
        s = np.ndarray((self.rect_num, 3))
        for i in range(self.rect_num):
            rand_width = np.random.randint(self.min_width, self.max_width + 1)
            rand_height = np.random.randint(self.min_height, self.max_height + 1)
            s[i, 0], s[i, 1], s[i, 2] = rand_height, rand_width, i + 1
        return BoxFillingSolutionRuleBased(rectangle_permutation=s, box_size=self.L)

    def is_feasible_sol(self, solution: BoxFillingSolutionRuleBased) -> bool:
        return np.unique(solution.solution[:, 2]).size == self.rect_num

    def is_feasible_value(self) -> bool: ...

    def choose_variable(self) -> Any: ...

    def assign_value(self) -> ProblemSolution: ...

    def get_values(self) -> list[Any]: ...
