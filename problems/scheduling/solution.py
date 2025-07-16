class ScheduleSolution:
    def __init__(self, task_assignments: list[int]):
        self.solution = task_assignments

    def __repr__(self):
        return f"ScheduleSolution({self.solution})"