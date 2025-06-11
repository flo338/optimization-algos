from copy import deepcopy
from typing import Any, Literal
import numpy as np
from app.optimization.local_search.instance import ProblemInstance
from app.optimization.local_search.meta_heuristics.hill_climbing import HillClimbing
from app.optimization.local_search.neighborhood import Neighborhood
from app.optimization.local_search.objective import Objective
from app.optimization.solution import ProblemSolution
from scipy.signal import convolve2d
from scipy.ndimage import convolve

POWER = 1.5

# Rectangle
# int x int x int x int x int
# y x 'x' x height x width x box x number


class BoxFillingSolutionRelaxedGeometric(ProblemSolution):
    def __init__(self, solution: np.ndarray) -> None:
        self.solution: np.ndarray = solution


class BoxFillingObjectiveRelaxedGeometric(Objective):
    def __init__(self, L: int, rect_num: int) -> None:
        self.L = L
        self.rect_num = rect_num
        self.step = 0
        self.cnt = False

    def obj(self, solution: list[BoxFillingSolutionRelaxedGeometric]) -> np.ndarray:
        objs = np.ndarray(len(solution))
        # num_rectangle = solution[0].solution.shape[0]
        for idx in range(len(solution)):
            unique_counts = np.bincount(solution[idx].solution[:, 4].astype(int))
            num_boxes = np.max(solution[idx].solution[:, 4])

            box_with_overlaps = np.zeros((int(num_boxes) + 1, self.L, self.L))
            for y, x, height, width, box, number in solution[idx].solution:
                box_with_overlaps[
                    int(box), int(y) : int(y + height), int(x) : int(x + width)
                ] += 1

            overlaps = box_with_overlaps[np.where(box_with_overlaps > 1)].sum()
            non_overlaps = box_with_overlaps[np.where(box_with_overlaps == 1)].sum()

            occ_space = np.array(
                [
                    len(np.nonzero(row)[0])
                    for row in box_with_overlaps.reshape(int(num_boxes) + 1, -1)
                ]
            )

            fraction = min(2, self.step / 50)
            objs[idx] = (
                np.sum(unique_counts)
                - num_boxes**3
                - overlaps * fraction
                + non_overlaps * fraction
                + np.sum(occ_space)
            )

        self.step = self.step + 1 if self.cnt else self.step
        self.cnt = not self.cnt
        return objs


class RelaxedGeometricNeighborhood(Neighborhood):
    def __init__(self, L: int) -> None:
        self.sol: BoxFillingSolutionRelaxedGeometric = (
            BoxFillingSolutionRelaxedGeometric(np.ndarray(1))
        )
        self.L = L
        self.step = 0
        self.steps_till_penalty = 50

    def get_neighbors(
        self,
        solution: BoxFillingSolutionRelaxedGeometric,
        method: Literal["exhaustive"] | Literal["stochastic"] = "exhaustive",
    ) -> list[BoxFillingSolutionRelaxedGeometric]:
        return self._get_neighbors_exhaustive(solution)

    def _get_neighbors_stochastic(
        self, solution: ProblemSolution
    ) -> list[BoxFillingSolutionRelaxedGeometric]:
        return []

    def _neighbor_generator(self, solution: BoxFillingSolutionRelaxedGeometric):
        solution = deepcopy(solution)
        max_box = solution.solution[:, 4].max()
        box_with_overlaps = np.zeros((int(max_box) + 2, self.L, self.L))
        for y, x, height, width, box, number in solution.solution:
            box_with_overlaps[
                int(box), int(y) : int(y + height), int(x) : int(x + width)
            ] += 1

        np.random.shuffle(solution.solution)
        for rect_ix in range(solution.solution.shape[0]):
            y, x, h, w, b, n = solution.solution[rect_ix]
            area = h * w
            kernel = np.ones((int(h), int(w)))
            convolution = np.array(
                [convolve2d(kernel, s, mode="valid") for s in box_with_overlaps]
            )
            allowed_fraction = max(0, (100 - self.step) / 100)
            candidates = np.column_stack(
                np.where(convolution <= area * allowed_fraction)
            )

            rectangles = deepcopy(solution.solution)
            for b, y, x in candidates:
                if b > max_box + 1:
                    break
                rectangles[rect_ix, 0] = y
                rectangles[rect_ix, 1] = x
                rectangles[rect_ix, 4] = b
                yield BoxFillingSolutionRelaxedGeometric(solution=rectangles)

        return []

    def _get_neighbors_exhaustive(
        self, solution: BoxFillingSolutionRelaxedGeometric
    ) -> list[BoxFillingSolutionRelaxedGeometric]:
        if self.sol == solution:
            return [next(self._generator)]

        self.step += 1

        self._generator = self._neighbor_generator(solution=solution)
        self.sol = solution
        return [next(self._generator)]


class BoxFillingInstanceRelaxedGeometric(ProblemInstance):
    def __init__(
        self,
        L: int,
        rect_num: int,
        max_width: int,
        max_height: int,
        min_width: int = 1,
        min_height: int = 1,
    ) -> None:
        self.neighborhood = RelaxedGeometricNeighborhood(L)
        self.objective = BoxFillingObjectiveRelaxedGeometric(L, rect_num)

        self.L = L
        self.rect_num = rect_num
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

    def _generate_feasible_solution(self) -> BoxFillingSolutionRelaxedGeometric:
        s = np.ndarray((self.rect_num, 6))
        for i in range(self.rect_num):
            rand_width = np.random.randint(self.min_width, self.max_width + 1)
            rand_height = np.random.randint(self.min_height, self.max_height + 1)
            s[i, 0], s[i, 1], s[i, 2], s[i, 3], s[i, 4], s[i, 5] = (
                0,
                0,
                rand_height,
                rand_width,
                0,
                i + 1,
            )
        return BoxFillingSolutionRelaxedGeometric(solution=s)

    def is_feasible_sol(self, solution: BoxFillingSolutionRelaxedGeometric) -> bool:
        return np.unique(solution.solution[:, 4]).size == self.rect_num

    def is_feasible_value(self) -> bool: ...

    def choose_variable(self) -> Any: ...

    def assign_value(self) -> ProblemSolution: ...

    def get_values(self) -> list[Any]: ...


def build_box(solution, L, needed_boxes: int):
    box_with_overlaps = np.zeros((needed_boxes, L, L))
    for y, x, height, width, box, number in solution:
        box_with_overlaps[
            int(box), int(y) : int(y + height), int(x) : int(x + width)
        ] = number

    return box_with_overlaps
