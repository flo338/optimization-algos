"""Defines a problem instance to sort a list of numbers as a figurative example"""

from collections import defaultdict
from copy import deepcopy
from itertools import chain
import random
from typing import Literal, Tuple
import numpy as np

from app.optimization.local_search.neighborhood import Neighborhood
from app.problems.box_filling.rectangle import Rectangle, RectangleFactory
from app.problems.box_filling.solution import BoxFillingSolution
from app.problems.box_filling.utils import (
    approximate_all_moves,
    generate_all_moves,
    get_blocked_fields,
    place_rectangle,
)


class GeometricNeighborhood(Neighborhood):
    def __init__(self, L: int) -> None:
        self.L = L

    def get_neighbors(
        self,
        solution: BoxFillingSolution,
        method: Literal["exhaustive", "probable_fields", "stochastic"] = "stochastic",
    ) -> list[BoxFillingSolution]:
        match method:
            case "exhaustive":
                return self._get_neighbors_exhaustive(solution=solution)
            case "probable_fields":
                return self._get_neighbors_probable_fields(solution=solution)
            case "stochastic":
                return self._get_neighbors_stochastic(solution=solution)
            case _:
                raise ValueError(f"method: {method} not available")

    def _get_neighbors_stochastic(
        self, solution: BoxFillingSolution, return_num: int = 1
    ) -> list[BoxFillingSolution]:
        """
        Generates a number of neighbors stochastically.

        1. Choose a box randomly. The boxes are weighted by the free area they still have (Free area - occupied area)
        2. Choose a rectangle out of each box randomly
        3. Try to place each rectangle in all boxes in a 'lower corner first' fashion
        """

        # Available area in a box
        L_squared = self.L**2

        # Consumed area in the boxes
        rect_total_areas = defaultdict(lambda: np.zeros(2))
        for rect in solution.solution:
            rect_total_areas[rect.box] += np.array([len(rect.coordinates), 1])
        num_boxes = len(rect_total_areas)

        # Create probabilities based on free area available
        box_weights_free = [
            (L_squared - rect_total_areas[ix][0]) for ix in range(num_boxes)
        ]
        box_weights = [(rect_total_areas[ix][0]) for ix in range(num_boxes)]
        total_weight_free = sum(box_weights_free)
        total_weight = sum(box_weights)
        box_probabilities_free = [
            weight / total_weight_free for weight in box_weights_free
        ]
        box_probabilities = [weight / total_weight for weight in box_weights]

        # Choose boxes (Default := 1)
        boxes = np.random.choice(num_boxes, size=1, p=box_probabilities_free)

        # Choose rectangles in chosen boxes (Default := 1)
        chosen_rectangles = [
            random.choice([rect for rect in solution.solution if rect.box == box])
            for box in boxes
        ]

        blocked_coordinates = get_blocked_fields(rectangles=solution.solution)
        moves: list[list[Rectangle]] = []
        rf = RectangleFactory()

        for rectangle in chosen_rectangles:
            rectangle_movements: list[Rectangle] = []
            for box in np.random.choice(
                range(num_boxes), size=min(num_boxes, return_num), p=box_probabilities
            ):
                rectangle_movements += place_rectangle(
                    rectangle=rectangle,
                    box=int(box),
                    L=self.L,
                    blocked_coordinates=blocked_coordinates,
                    rf=rf,
                )
            moves.append(rectangle_movements)

        solutions: list[BoxFillingSolution] = []
        for rectangle_moves in moves:
            if len(rectangle_moves) == 0:
                continue
            rectangle_index = rectangle_moves[0].index
            competitors = [
                rect for rect in solution.solution if rect.index != rectangle_index
            ]
            for move in rectangle_moves:
                solutions.append(BoxFillingSolution(solution=competitors + [move]))

        return solutions

    def _get_neighbors_exhaustive(
        self, solution: BoxFillingSolution
    ) -> list[BoxFillingSolution]:
        rectangles: list[Rectangle] = solution.solution
        blocked_fields: set[Tuple[int, int, int]] = get_blocked_fields(
            rectangles=rectangles
        )
        num_boxes = max(rect.box for rect in rectangles) + 1

        neighbors_list = []

        for ix in range(len(rectangles)):
            iter_rectangles = deepcopy(rectangles)
            target: Rectangle = iter_rectangles[ix]
            competitors: set[Tuple[int, int, int]] = blocked_fields.difference(
                target.coordinates
            )

            moves: list[Rectangle] = generate_all_moves(
                rectangle=target, num_boxes=num_boxes, L=self.L
            )

            valid_movings = [
                move for move in moves if not move.coordinates.intersection(competitors)
            ]

            neighbors_list.append(
                [
                    BoxFillingSolution(
                        solution=iter_rectangles[:ix]
                        + [moved_rectangle]
                        + iter_rectangles[ix + 1 :]
                    )
                    for moved_rectangle in valid_movings
                ]
            )

        neighbors = list(chain(*neighbors_list))

        return neighbors

    def _get_neighbors_probable_fields(
        self, solution: BoxFillingSolution
    ) -> list[BoxFillingSolution]:
        """
        Implements an exhaustive approach, where only fields adjacent to current rectangles are considered.
        """
        rectangles: list[Rectangle] = solution.solution
        blocked_fields: set[Tuple[int, int, int]] = get_blocked_fields(
            rectangles=rectangles
        )

        neighbors_list = []

        for ix in range(len(rectangles)):
            iter_rectangles = deepcopy(rectangles)
            target: Rectangle = iter_rectangles[ix]
            competitors: set[Tuple[int, int, int]] = blocked_fields.difference(
                target.coordinates
            )

            moves: list[Rectangle] = approximate_all_moves(
                L=self.L, rectangle=target, blocked_fields=competitors
            )

            valid_movings = [
                move for move in moves if not move.coordinates.intersection(competitors)
            ]

            neighbors_list.append(
                [
                    BoxFillingSolution(
                        solution=iter_rectangles[:ix]
                        + [moved_rectangle]
                        + iter_rectangles[ix + 1 :]
                    )
                    for moved_rectangle in valid_movings
                ]
            )

        neighbors = list(chain(*neighbors_list))

        return neighbors
