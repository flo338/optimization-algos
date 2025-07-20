from itertools import combinations, product
import random
from optimization.local_search.neighborhood import Neighborhood
from optimization.solution import ProblemSolution
from problems.scheduling.solution import ScheduleSolution


class TaskSchedulingNeighborhood(Neighborhood):
    def __init__(
        self,
        num_workers: int,
        task_durations: list[int],
        max_worker_load: int,
        filter_feasible: bool = True,
        max_changes: int = 2,
    ):
        self.num_workers = num_workers
        self.task_durations = task_durations
        self.max_worker_load = max_worker_load
        self.filter_feasible = filter_feasible
        self.max_changes = max_changes

    def _is_feasible(self, solution: ProblemSolution) -> bool:
        assignment = solution.solution
        loads = [0 for _ in range(self.num_workers)]
        for task_idx, worker_id in enumerate(assignment):
            loads[worker_id] += self.task_durations[task_idx]
        return all(load <= self.max_worker_load for load in loads)


class HillClimbingNeighborhood(TaskSchedulingNeighborhood):
    def __init__(
        self,
        num_workers: int,
        task_durations: list[int],
        max_worker_load: int,
        filter_feasible: bool = True,
        max_changes: int = 2,
    ):
        super().__init__(
            num_workers, task_durations, max_worker_load, filter_feasible, max_changes
        )

    def get_neighbors(self, solution: ProblemSolution) -> list[ProblemSolution]:
        assignment = solution.solution
        num_tasks = len(assignment)
        neighbors = []

        for k in range(1, self.max_changes + 1):
            for task_indices in combinations(range(num_tasks), k):
                for new_workers in product(range(self.num_workers), repeat=k):
                    if all(
                        assignment[i] == new_workers[j]
                        for j, i in enumerate(task_indices)
                    ):
                        continue

                    new_assignment = assignment[:]
                    for j, i in enumerate(task_indices):
                        new_assignment[i] = new_workers[j]

                    neighbor = ScheduleSolution(new_assignment)

                    neighbors.append(neighbor)

        return neighbors


class SimulatedAnnealingNeighborhood(TaskSchedulingNeighborhood):
    def __init__(
        self,
        num_workers: int,
        task_durations: list[int],
        max_worker_load: int,
        filter_feasible: bool = True,
        max_changes: int = 2,
        num_samples: int = 100,
    ):
        super().__init__(
            num_workers, task_durations, max_worker_load, filter_feasible, max_changes
        )
        self.num_samples = num_samples

    def get_neighbors(self, solution: ProblemSolution) -> list[ProblemSolution]:
        assignment = solution.solution
        num_tasks = len(assignment)
        neighbors = []

        for _ in range(self.num_samples):
            new_assignment = assignment[:]

            k = random.randint(1, self.max_changes)

            tasks_to_change = random.sample(range(num_tasks), k)

            for task_idx in tasks_to_change:
                current_worker = new_assignment[task_idx]
                possible_workers = [
                    w for w in range(self.num_workers) if w != current_worker
                ]
                new_worker = random.choice(possible_workers)
                new_assignment[task_idx] = new_worker

            neighbor = ScheduleSolution(new_assignment)
            neighbors.append(neighbor)

        return neighbors
