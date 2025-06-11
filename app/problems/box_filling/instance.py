from enum import Enum
from typing import Generator, Tuple

import numpy as np
from app.optimization.local_search.instance import (
    ErrorWhileGeneratingSolution,
    ProblemInstance,
)
from app.optimization.solution import ProblemSolution
from app.problems.box_filling.local_search.neighborhoods.geometric_neighborhood import (
    GeometricNeighborhood,
)
from app.problems.box_filling.local_search.objectives import BoxFillingObjective
from app.problems.box_filling.rectangle import Rectangle, RectangleFactory
from app.problems.box_filling.solution import BoxFillingSolution
from app.problems.box_filling.utils import get_blocked_fields, get_coordinates


class Rotation(Enum):
    TRUE = 1
    FALSE = 0


class BoxFilling(ProblemInstance):
    def __init__(
        self,
        L: int,
        rect_num: int,
        max_width: int,
        max_height: int,
        min_width: int = 1,
        min_height: int = 1,
        box_limit: int = 1000,
    ):
        self.L = L
        self.rect_num = rect_num
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height
        self.box_limit = box_limit

        self.neighborhood = GeometricNeighborhood(L=L)
        self.objective = BoxFillingObjective()

    def generate_feasible_solution(self) -> BoxFillingSolution:
        return super().generate_feasible_solution()  # type: ignore

    def _generate_feasible_solution(self) -> BoxFillingSolution:
        if self.max_width > self.L or self.max_height > self.L:
            raise ErrorWhileGeneratingSolution(
                "Rectangles can't be bigger than the box size"
            )

        rf = RectangleFactory()
        rectangles: list[Rectangle] = []
        last_available_right_field = 0
        last_box = 0

        for index in range(self.rect_num):
            rand_width = np.random.randint(
                self.min_width, self.max_width + 1
            )  # last element excluded
            rand_height = np.random.randint(
                self.min_height, self.max_height + 1
            )  # last element excluded

            if last_available_right_field + rand_width > self.L:
                top_left_corner = (self.L - rand_height, 0)
                last_box += 1
                last_available_right_field = rand_width
                rectangles.append(
                    rf.create_from_width_height(
                        width=rand_width,
                        height=rand_height,
                        top_left_corner=top_left_corner,
                        box=last_box,
                        index=index + 1,
                    )
                )
                continue

            top_left_corner = (self.L - rand_height, last_available_right_field)
            last_available_right_field += rand_width
            rectangles.append(
                rf.create_from_width_height(
                    width=rand_width,
                    height=rand_height,
                    top_left_corner=top_left_corner,
                    box=last_box,
                    index=index + 1,
                )
            )

        return BoxFillingSolution(solution=rectangles)

    def is_feasible_sol(self, solution: BoxFillingSolution) -> bool:
        rectangles: list[Tuple[int, int, int]] = [
            coords for rect in solution.solution for coords in rect.coordinates
        ]

        return len(rectangles) == len(set(rectangles))

    def is_feasible_value(
        self,
        val: Tuple[int, int, int, Rotation],
        var: Rectangle,
        solution: BoxFillingSolution,
    ) -> bool:
        """Checks if specific value is feasible for variable given a partial solution"""
        blocked_coordinates = get_blocked_fields(solution.solution)

        rotation: Rotation = val[3]
        row, col = val[1], val[2]
        if rotation.value:
            if (
                val[0] < self.box_limit
                and var.width + row - 1 < self.L
                and var.height + col - 1 < self.L
                and get_coordinates(
                    width=var.height,
                    height=var.width,
                    top_left_corner=(row, col),
                    box=val[0],
                ).isdisjoint(blocked_coordinates)
            ):
                return True
        else:
            if (
                val[0] < self.box_limit
                and var.height + row - 1 < self.L
                and var.width + col - 1 < self.L
                and get_coordinates(
                    width=var.width,
                    height=var.height,
                    top_left_corner=(row, col),
                    box=val[0],
                ).isdisjoint(blocked_coordinates)
            ):
                return True
        return False

    def assign_value(
        self,
        val: Tuple[int, int, int, Rotation],
        var: Rectangle,
        solution: BoxFillingSolution,
    ) -> ProblemSolution:
        """Assigns a value to a variable and returns new partial solution"""
        new_var = (
            RectangleFactory.create_from_width_height(
                width=var.height,
                height=var.width,
                top_left_corner=(val[1], val[2]),
                box=val[0],
                index=var.index,
            )
            if val[3].value
            else RectangleFactory.create_from_width_height(
                width=var.width,
                height=var.height,
                top_left_corner=(val[1], val[2]),
                box=val[0],
                index=var.index,
            )
        )
        solution.solution += [new_var]

        return solution

    def get_values(
        self,
        var: Rectangle,
        solution: BoxFillingSolution,
        pruned_vals: set[Tuple[int, int, int, Rotation]],
    ) -> Generator:
        """returns values starting from box zero. top left corner."""
        num_boxes = (
            max(rect.box for rect in solution.solution) + 1 if solution.solution else 0
        )

        blocked_coordinates = get_blocked_fields(solution.solution)

        hulls: set[Tuple[int, int, int]] = set().union(*[var.hull for var in solution.solution])  # type: ignore
        hull_cords = hulls.difference(blocked_coordinates)
        for box, row, col in sorted(list(hull_cords)):
            if 0 <= row < self.L - var.height + 1:
                if 0 <= col < self.L - var.width + 1:
                    if (box, row, col, Rotation.FALSE) not in pruned_vals:
                        yield (box, row, col, Rotation.FALSE)
        # Add new box as value
        new_box_value = (num_boxes, 0, 0, Rotation.FALSE)
        if new_box_value not in pruned_vals:
            yield new_box_value

    def choose_variable(
        self, vars: set[Rectangle], solution: ProblemSolution
    ) -> Rectangle:
        """Chooses rectangles by biggest area"""
        vars_list = list(vars)
        vars_list.sort(key=lambda rect: rect.height * rect.width, reverse=True)
        return vars_list[0]


class BoxFillingFactory:
    @staticmethod
    def get_instance(
        L: int,
        rect_num: int,
        max_width: int,
        max_height: int,
        min_width: int = 1,
        min_height: int = 1,
        box_limit: int = 1000,
    ) -> BoxFilling:
        return BoxFilling(
            L=L,
            rect_num=rect_num,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            box_limit=box_limit,
        )
