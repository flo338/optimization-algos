from dataclasses import dataclass
from typing import Tuple

import numpy as np


def get_coordinates(
    width: int, height: int, box: int, top_left_corner: Tuple[int, int]
) -> set[Tuple[int, int, int]]:
    return {
        (box, row, column)
        for row in range(
            top_left_corner[0], top_left_corner[0] + height
        )  # as last element is exclusive add one
        for column in range(
            top_left_corner[1], top_left_corner[1] + width
        )  # as last element is exclusive add one
    }


def get_hull(
    width: int, height: int, box: int, top_left_corner: Tuple[int, int]
) -> set[Tuple[int, int, int]]:
    hull = {
        (box, row, top_left_corner[1] - 1)
        for row in range(top_left_corner[0] - 1, top_left_corner[0] + height + 1)
    }
    hull = hull.union(
        {
            (box, row, top_left_corner[1] + width)
            for row in range(top_left_corner[0] - 1, top_left_corner[0] + height + 1)
        }
    )
    hull = hull.union(
        {
            (box, top_left_corner[0] - 1, col)
            for col in range(top_left_corner[1] - 1, top_left_corner[1] + width + 1)
        }
    )
    hull = hull.union(
        {
            (box, top_left_corner[0] + height, col)
            for col in range(top_left_corner[1] - 1, top_left_corner[1] + width + 1)
        }
    )

    return hull


@dataclass(frozen=True, eq=True)
class Rectangle:
    width: int
    height: int
    coordinates: set[Tuple[int, int, int]]
    box: int
    top_left_corner: Tuple[int, int]
    hull: set[Tuple[int, int, int]] | None = None
    index: int | None = None

    def __hash__(self):
        return hash((self.index,))


class RectangleFactory:
    """
    Creates and modifies rectangles.
    As Rectangles are immutable, when modifying a new instance of Rectangle is returned.
    """

    @staticmethod
    def create_from_width_height(
        width: int,
        height: int,
        top_left_corner: Tuple[int, int],
        box: int,
        index: int | None = None,
    ) -> Rectangle:
        coordinates = get_coordinates(
            width=width,
            height=height,
            box=box,
            top_left_corner=top_left_corner,
        )
        hull = get_hull(
            width=width,
            height=height,
            box=box,
            top_left_corner=top_left_corner,
        )

        return Rectangle(
            width=width,
            height=height,
            top_left_corner=top_left_corner,
            box=box,
            coordinates=coordinates,
            index=index,
            hull=hull,
        )

    def create_from_coordinates(
        self, coordinates: set[Tuple[int, int, int]], index: int | None = None
    ) -> Rectangle:
        coordinates_arr = np.asarray(list(coordinates))
        box: int = int(coordinates_arr[0, 0])
        top_left_corner = (
            int(coordinates_arr[:, 1].min()),
            int(coordinates_arr[:, 2].min()),
        )
        height = int(coordinates_arr[:, 1].max()) - int(coordinates_arr[:, 1].min()) + 1
        width = int(coordinates_arr[:, 2].max()) - int(coordinates_arr[:, 2].min()) + 1
        return Rectangle(
            width=width,
            height=height,
            top_left_corner=top_left_corner,
            coordinates=coordinates,
            box=box,
            index=index,
        )
