import unittest

from app.problems.box_filling.rectangle import RectangleFactory, get_coordinates
from app.problems.box_filling.solution import BoxFillingSolution


class TestBoxFilling(unittest.TestCase):
    def test_get_coordinates(self):
        coords = get_coordinates(width=2, height=2, box=0, top_left_corner=(1, 1))
        assert coords == {(0, 1, 1), (0, 1, 2), (0, 2, 2), (0, 2, 1)}

        coords = get_coordinates(width=2, height=1, box=0, top_left_corner=(2, 2))
        assert coords == {(0, 2, 2), (0, 2, 3)}

    def test_rectangle_factory(self):
        rf = RectangleFactory()

        coordinates = {(0, 1, 1), (0, 1, 2), (0, 2, 1), (0, 2, 2)}

        rect1 = rf.create_from_coordinates(coordinates=coordinates)

        rect2 = rf.create_from_width_height(
            width=2, height=2, top_left_corner=(1, 1), box=0
        )

        assert rect1 == rect2

    def test_reduce_boxes(self):
        rf = RectangleFactory()

        coordinates1 = {(0, 1, 1), (0, 1, 2), (0, 2, 1), (0, 2, 2)}
        coordinates2 = {(3, 1, 1), (3, 1, 2), (3, 2, 1), (3, 2, 2)}

        rect1 = rf.create_from_coordinates(coordinates=coordinates1)
        rect2 = rf.create_from_coordinates(coordinates=coordinates2)

        sol = BoxFillingSolution(solution=[rect1, rect2])

        sol = sol.reduce_boxes()

        assert {sol[0].box, sol[1].box} == {0, 1}
