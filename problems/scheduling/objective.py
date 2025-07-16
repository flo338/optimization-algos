from optimization.solution import ProblemSolution


class LoadBalancingObjective:
    def __init__(self, task_durations: list[int], max_worker_load: int):
        self.task_durations = task_durations
        self.max_worker_load = max_worker_load

    def _worker_loads(self, assignment: list[int], num_workers: int) -> list[int]:
        loads = [0 for _ in range(num_workers)]
        for task_idx, worker_id in enumerate(assignment):
            loads[worker_id] += self.task_durations[task_idx]
        return loads

    @staticmethod
    def _variance(loads: list[int]) -> float:
        mean = sum(loads) / len(loads)
        return sum((x - mean) ** 2 for x in loads) / len(loads)

    def obj(self, solutions: list[ProblemSolution]) -> list[float]:
        results = []
        for sol in solutions:
            assignment = sol.solution
            num_workers = max(assignment) + 1
            loads = self._worker_loads(assignment, num_workers)
            overload_penalty = sum(
                max(0, load - self.max_worker_load) ** 2 for load in loads
            )
            variance_score = self._variance(loads)
            total_score = variance_score + 10 * overload_penalty  # weighted penalty
            results.append(1e6-total_score)
        return results