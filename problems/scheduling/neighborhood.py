from itertools import combinations, product
import random
from typing import Literal
from optimization.solution import ProblemSolution
from problems.scheduling.solution import ScheduleSolution


class TaskReassignmentNeighborhood:
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

    def get_neighbors(
        self,
        solution: ProblemSolution,
        method: Literal["exhaustive", "stochastic"] = "stochastic",
    ) -> list[ProblemSolution]:
        """return neighbors given a certain method."""
        match method:
            case "exhaustive":
                return self._get_neighbors_exhaustive(solution=solution)
            case "stochastic":
                return self._get_neighbors_stochastic(solution=solution)
            case _:
                raise ValueError(f"method: {method} not available")


    def _get_neighbors_exhaustive(self, solution: ProblemSolution) -> list[ProblemSolution]:
        assignment = solution.solution
        num_tasks = len(assignment)
        neighbors = []

        # Iterate over all sets of up to `max_changes` task indices
        for k in range(1, self.max_changes + 1):
            for task_indices in combinations(range(num_tasks), k):
                # For each such combination of tasks, try assigning them to all possible new workers
                for new_workers in product(range(self.num_workers), repeat=k):
                    # Skip if it's the same as current assignments
                    if all(assignment[i] == new_workers[j] for j, i in enumerate(task_indices)):
                        continue

                    new_assignment = assignment[:]
                    for j, i in enumerate(task_indices):
                        new_assignment[i] = new_workers[j]

                    neighbor = ScheduleSolution(new_assignment)

                    #if not self.filter_feasible or self._is_feasible(neighbor):
                    neighbors.append(neighbor)

        return neighbors

    def _is_feasible(self, solution: ProblemSolution) -> bool:
        assignment = solution.solution
        loads = [0 for _ in range(self.num_workers)]
        for task_idx, worker_id in enumerate(assignment):
            loads[worker_id] += self.task_durations[task_idx]
        return all(load <= self.max_worker_load for load in loads)

    def _get_neighbors_stochastic(
        self,
        solution: ProblemSolution,
        num_samples: int = 100,
    ) -> list[ProblemSolution]:
        assignment = solution.solution
        num_tasks = len(assignment)
        neighbors = []

        for _ in range(num_samples):
            new_assignment = assignment[:]

            # Randomly choose how many tasks to change (1 to max_changes)
            k = random.randint(1, self.max_changes)

            # Randomly select k distinct task indices to change
            tasks_to_change = random.sample(range(num_tasks), k)

            for task_idx in tasks_to_change:
                current_worker = new_assignment[task_idx]
                # Randomly select a different worker
                possible_workers = [w for w in range(self.num_workers) if w != current_worker]
                new_worker = random.choice(possible_workers)
                new_assignment[task_idx] = new_worker

            neighbor = ScheduleSolution(new_assignment)
          #  if not self.filter_feasible or self._is_feasible(neighbor):
            neighbors.append(neighbor)

        return neighbors