"""Implements the hill climbing meta heuristic."""

import numpy as np
from app.optimization.local_search.local_search import LocalSearch


class HillClimbing(LocalSearch):
    """
    Hill climbing is a meta heuristic using the local search heuristic.
    The next solution is chosen by greedily updating to the neighbor that improves the objective the most.
    """

    _method = "exhaustive"

    def __init__(self, instance, steps):
        super().__init__(instance, steps)

    def _choose(self, obj_diffs: np.ndarray) -> list[int]:
        argmax = np.argmax(obj_diffs).astype(int)

        if obj_diffs[argmax] <= 0:
            return []

        self._tries = 0
        return [argmax]

    def get_current_info(self, curr_obj: float):
        return f"step: {self._curr_step}\nobj: {curr_obj}\n\n"
