import numpy as np
from optimization.solution import ProblemSolution
from problems.box_filling.rectangle import Rectangle, RectangleFactory


class BoxFillingSolution(ProblemSolution):
    solution: list[Rectangle]

    def __init__(self, solution: list[Rectangle]) -> None:
        self.solution = solution

    def reduce_boxes(self) -> list[Rectangle]:
        """
        We have a number of boxes, which have indices from 0 until number of boxes.
        If boxes get empty, eg. box 7, then we want that all indices over 7 move down one
        such that the gap is filled.
        This function implements this logic.
        """
        used_boxes = set()
        biggest_box = 0

        for rect in self.solution:
            biggest_box = max(rect.box, biggest_box)
            used_boxes.add(rect.box)
        biggest_box += 1

        if biggest_box == used_boxes:
            return self.solution

        index_map: dict[int, int] = dict(
            zip(np.sort(list(used_boxes)).tolist(), list(range(len(used_boxes))))
        )  # type: ignore

        rf = RectangleFactory()
        sol_with_mapped_boxes = [
            rf.create_from_width_height(
                width=rect.width,
                height=rect.height,
                index=rect.index,
                top_left_corner=rect.top_left_corner,
                box=index_map[rect.box],
            )
            for rect in self.solution
        ]

        self.solution = sol_with_mapped_boxes

        return self.solution
