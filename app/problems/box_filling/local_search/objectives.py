from collections import defaultdict
from app.optimization.local_search.objective import Objective
from app.problems.box_filling.solution import BoxFillingSolution

POWER = 1.1


class BoxFillingObjective(Objective):
    @staticmethod
    def get_best_objective(num_rect: int):
        return num_rect**1.1

    def obj(self, solution: list[BoxFillingSolution]) -> list[float]:
        """
        Objective function consists of:
            - subtracting the number of boxes needed
            - Squaring the number of all rectangles in each box and adding up
              ∑_{b in boxes} num_rectangles(b)**2
              x**c with c>1 is strictly convex. The sum of these squares therefore gets bigger,
              if squares are more accumulated in one box vs. spread over multiple.

              eg. 2^2 + 3^2 < (2 + 3)^2
                  <=> 13 < 25

        Total objective function: obj(Solution) = - #Boxes + ∑_{b in Boxes} num_rectangles(b)**2
        """

        num_boxes: list[int] = []
        num_rects: list[float] = []

        for s in solution:
            num_box = 0
            num_rect = defaultdict(float)
            for rect in s.solution:
                num_box = max(num_box, rect.box)
                num_rect[rect.box] += 1.0
            num_boxes.append(num_box + 1)
            num_rects.append(sum(num**POWER for num in num_rect.values()))

        # objective = - number of boxes + score function described above
        return [-1 * num_boxes[ix] + num_rects[ix] for ix in range(len(solution))]
