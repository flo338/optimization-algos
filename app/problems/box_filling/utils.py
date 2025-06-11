from typing import Tuple

from app.problems.box_filling.rectangle import (
    Rectangle,
    RectangleFactory,
    get_coordinates,
)


def get_adjancencies(i: int, j: int, box: int, L: int) -> set[Tuple[int, int, int]]:
    """Get adjacent indices for a coordinate"""
    adjacent: set[Tuple[int, int, int]] = set()
    if j > 0:
        adjacent.update({(box, i, j - 1)})
    if j < L - 1:
        adjacent.update({(box, i, j + 1)})
    if i > 0:
        adjacent.update({(box, i - 1, j)})
    if i < L - 1:
        adjacent.update({(box, i + 1, j)})
    return adjacent


def place_rectangle(
    rectangle: Rectangle,
    rf: RectangleFactory,
    box: int,
    L: int,
    blocked_coordinates: set[Tuple[int, int, int]],
) -> list[Rectangle]:
    """
    Place a rectangle in a bottom left first fashion.
    Specifically we search the first spot we can fit a rectangle or its 90° rotation from
    the bottom left on.
    """
    rectangle_movements: list[Rectangle] = []
    box_completed = False
    for row in range(L - 1, -1, -1):
        for col in range(0, L):
            if rectangle.height + row - 1 < L and rectangle.width + col < L:
                cand_rect = rf.create_from_width_height(
                    width=rectangle.width,
                    height=rectangle.height,
                    top_left_corner=(row, col),
                    box=box,
                    index=rectangle.index,
                )
                if len(cand_rect.coordinates.intersection(blocked_coordinates)) == 0:
                    rectangle_movements.append(cand_rect)
                    box_completed = True

            if rectangle.height + col - 1 < L and rectangle.width + row < L:
                cand_rect = rf.create_from_width_height(
                    width=rectangle.height,
                    height=rectangle.width,
                    top_left_corner=(row, col),
                    box=box,
                    index=rectangle.index,
                )
                if len(cand_rect.coordinates.intersection(blocked_coordinates)) == 0:
                    rectangle_movements.append(cand_rect)
                    box_completed = True

            if box_completed:
                return rectangle_movements
    return []


def is_valid_placement(
    rectangle: Rectangle,
    L: int,
    blocked_coordinates: set[Tuple[int, int, int]],
) -> bool:
    row, col = rectangle.top_left_corner
    if (
        rectangle.height + row - 1 < L
        and rectangle.width + col < L
        and get_coordinates(
            width=rectangle.width,
            height=rectangle.height,
            top_left_corner=(row, col),
            box=rectangle.box,
        ).isdisjoint(blocked_coordinates)
    ):
        return True
    return False


def approximate_all_moves(
    rectangle: Rectangle, blocked_fields: set[Tuple[int, int, int]], L: int
) -> list[Rectangle]:
    """
    Approximates the most important moves by searching only on adjacent fields
    to current rectangles. Less expensive than `_generate_all_moves`
    """

    probable_fields: set[Tuple[int, int, int]] = set().union(
        *[
            get_adjancencies(i=field[1], j=field[2], box=field[0], L=L)
            for field in blocked_fields
        ]
    )
    probable_fields.difference_update(blocked_fields)
    rf = RectangleFactory()

    moves: list[Rectangle] = []

    for field in probable_fields:
        field_moves: list[Rectangle] = []
        if rectangle.height + field[1] - 1 < L and rectangle.width + field[2] < L:
            field_moves.append(
                rf.create_from_width_height(
                    width=rectangle.width,
                    height=rectangle.height,
                    top_left_corner=(field[1], field[2]),
                    box=field[0],
                    index=rectangle.index,
                )
            )
        if rectangle.height + field[2] - 1 < L and rectangle.width + field[1] < L:
            field_moves.append(
                rf.create_from_width_height(
                    width=rectangle.height,
                    height=rectangle.width,
                    top_left_corner=(field[1], field[2]),
                    box=field[0],
                    index=rectangle.index,
                )
            )
        if field[1] - rectangle.width + 1 >= 0 and field[2] + rectangle.height - 1 < L:
            field_moves.append(
                rf.create_from_width_height(
                    width=rectangle.height,
                    height=rectangle.width,
                    top_left_corner=(field[1] - rectangle.width + 1, field[2]),
                    box=field[0],
                    index=rectangle.index,
                )
            )
        if field[2] - rectangle.width + 1 >= 0 and field[1] + rectangle.height - 1 < L:
            field_moves.append(
                rf.create_from_width_height(
                    width=rectangle.width,
                    height=rectangle.height,
                    top_left_corner=(field[1], field[2] - rectangle.width + 1),
                    box=field[0],
                    index=rectangle.index,
                )
            )
        moves += field_moves

    return moves


def generate_all_moves(rectangle: Rectangle, num_boxes: int, L: int) -> list[Rectangle]:
    """
    Generates all moves for a given rectangle.
    This approach performs exhaustive search and is computationally very expensive.
    """
    rf = RectangleFactory()

    moves: list[Rectangle] = [
        rf.create_from_width_height(
            width=rectangle.width,
            height=rectangle.height,
            box=box,
            top_left_corner=(row, column),
            index=rectangle.index,
        )
        for box in range(max(0, rectangle.box - 1, min(num_boxes, rectangle.box + 1)))
        for row in range(0, L - rectangle.height + 1)
        for column in range(0, L - rectangle.width + 1)
    ]

    if rectangle.width != rectangle.height:
        rotated_moves: list[Rectangle] = [
            rf.create_from_width_height(
                width=rectangle.height,
                height=rectangle.width,
                box=box,
                top_left_corner=(row, column),
                index=rectangle.index,
            )
            for box in range(
                max(0, rectangle.box - 1, min(num_boxes, rectangle.box + 1))
            )
            for row in range(0, L - rectangle.width + 1)
            for column in range(0, L - rectangle.height + 1)
        ]
        return moves + rotated_moves

    return moves


def get_blocked_fields(rectangles: list[Rectangle]) -> set[Tuple[int, int, int]]:
    """Returns all fields with rectangles blocking them."""
    blocked_fields = set()
    for rectangle in rectangles:
        blocked_fields.update(rectangle.coordinates)
    return blocked_fields
