from enum import StrEnum
import numpy as np
from app.optimization.local_search.local_search import LocalSearch


class CoolingSchedule(StrEnum):
    LOG = "Logarithmic"
    GEOMETRIC = "Geometric"


class SimulatedAnnealing(LocalSearch):
    _method = "stochastic"
    _T: float
    _last_obj: float
    _cooling_schedule: CoolingSchedule
    alpha: float = 0.99
    C: float = 50.0

    def __init__(
        self,
        instance,
        steps,
        temperature: float,
        alpha: float = 0.99,
        C: float = 50.0,
        cooling_schedule: CoolingSchedule = CoolingSchedule.GEOMETRIC,
    ):
        super().__init__(instance, steps)
        self.alpha = alpha
        self.C = C
        self._T = temperature
        self._cooling_schedule = cooling_schedule

    def _choose(self, obj_diffs: np.ndarray) -> list[int]:
        if obj_diffs[0] > 0:
            return [0]

        match self._cooling_schedule:
            case CoolingSchedule.GEOMETRIC:
                self._T = self._geometric_cooling(
                    step=self._curr_step, alpha=self.alpha, T=self._T
                )
            case CoolingSchedule.LOG:
                self._T = self._log_cooling(step=self._curr_step, C=self.C)

        return (
            [0]
            if np.random.uniform(0, 1) < np.exp(obj_diffs[0] / (self._T + 1e-2))
            else []
        )

    @staticmethod
    def _geometric_cooling(step: int, alpha: float, T: float) -> float:
        """
        Implements a geometric cooling schedule

        T_step = T_step-1 * alpha^step
        """
        return T * alpha**step

    @staticmethod
    def _log_cooling(step: int, C: float) -> float:
        """
        Implements logarithmic cooling

        T_step = C / log(1+step)
        """
        return C / np.log(1 + step)

    def get_current_info(self, curr_obj: float) -> str:
        return f"step: {self._curr_step}\nobj: {curr_obj:.3f}\ntemperature: {self._T:.3f}\n\n"
