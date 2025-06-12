from typing import Tuple

from problems.box_filling.rectangle import (
    Rectangle,
    RectangleFactory,
)

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
