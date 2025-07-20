from ctypes import ArgumentError
import random
from typing import Literal
from optimization.local_search.instance_local_search import ProblemInstanceLocalSearch
from optimization.solution import ProblemSolution
from problems.scheduling.neighborhood import (
    HillClimbingNeighborhood,
    SimulatedAnnealingNeighborhood,
)
from problems.scheduling.objective import LoadBalancingObjective
from problems.scheduling.solution import ScheduleSolution


class ErrorWhileGeneratingSolution(Exception):
    pass


class LocalSearchInstance(ProblemInstanceLocalSearch):
    def __init__(
        self,
        task_durations: list[int],
        num_workers: int,
        max_worker_load: int,
        meta_heuristic: Literal["Hill Climbing", "Simulated Annealing"],
    ) -> None:
        self.task_durations = task_durations
        self.num_workers = num_workers
        self.max_worker_load = max_worker_load

        match meta_heuristic:
            case "Hill Climbing":
                self.neighborhood = HillClimbingNeighborhood(
                    num_workers=num_workers,
                    task_durations=task_durations,
                    max_worker_load=max_worker_load,
                    filter_feasible=True,
                )
            case "Simulated Annealing":
                self.neighborhood = SimulatedAnnealingNeighborhood(
                    num_workers=num_workers,
                    task_durations=task_durations,
                    max_worker_load=max_worker_load,
                    filter_feasible=True,
                )
            case _:
                raise ArgumentError(
                    f"{meta_heuristic} is not a valid meta heuristic of local search."
                )

        self.objective = LoadBalancingObjective(
            task_durations=task_durations,
            max_worker_load=max_worker_load,
        )

    def generate_feasible_solution(self) -> ProblemSolution:
        try:
            return self._generate_feasible_solution()
        except Exception as e:
            raise ErrorWhileGeneratingSolution("Can't find feasible solution") from e

    def _generate_feasible_solution(self) -> ProblemSolution:
        max_attempts = 1000
        num_tasks = len(self.task_durations)
        for _ in range(max_attempts):
            candidate = [
                random.randint(0, self.num_workers - 1) for _ in range(num_tasks)
            ]
            if self.is_feasible_sol(ScheduleSolution(candidate)):
                return ScheduleSolution(candidate)
        raise ErrorWhileGeneratingSolution("Exceeded max attempts")

    def is_feasible_sol(self, solution: ProblemSolution) -> bool:
        #        return True
        assignment = solution.solution
        if not assignment:
            return False
        loads = [0 for _ in range(self.num_workers)]
        for task_idx, worker_id in enumerate(assignment):
            loads[worker_id] += self.task_durations[task_idx]
        return all(load <= self.max_worker_load for load in loads)
