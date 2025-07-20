from collections import defaultdict
from copy import deepcopy
from typing import Any
from optimization.backtracking.instance_backtracking import ProblemInstanceBacktracking
from optimization.exceptions import ErrorDuringStep, ErrorNoImprovement, ErrorNoVars
from optimization.solution import ProblemSolution


class ErrorCantFindSolution(Exception): ...


Variable = Any
Value = Any


class Backtracking:
    _instance: ProblemInstanceBacktracking
    _steps: int
    _curr_step: int = 0

    _vars: set[Variable]

    def __init__(
        self, instance: ProblemInstanceBacktracking, vars: set, steps: int = 500
    ):
        self._instance = instance
        self._steps = steps
        self._vars = vars

        self._set_up()

    def _set_up(self):
        self._level: int = 0
        self._pruned_vals: defaultdict[Variable, set[Value]] = defaultdict(set)
        self._available_vals_at_level: dict[int, set[Value]] = {}
        self._assigned_val_at_level: dict[int, tuple[Variable, Value]] = {}
        self._solution_at_level: dict[int, ProblemSolution] = {}

    def get_current_info(self, **kwargs):
        return f"{self._curr_step} / {self._steps}\n\n"

    def search(self, start_sol: ProblemSolution | None = None) -> ProblemSolution:
        s = (
            start_sol
            if start_sol and self._instance.is_feasible_sol(start_sol)
            else self._instance.generate_feasible_solution()
        )

        for step in range(self._curr_step, self._steps):
            if s is None:
                raise ErrorDuringStep("Backtracking.step(...) returned None")
            try:
                s = self.step(curr_sol=s)
            except ErrorNoImprovement:
                return s

        return s

    def step(self, curr_sol: ProblemSolution) -> ProblemSolution:
        """
        Performs one step of backtracking search.
        The step can either be an assignment of a value to a variable or a backtracking step.
        Takes empty solution as first curr_sol.
        """
        if not self._vars:
            self._pruned_vals = defaultdict(set)
            self._set_up()
            raise ErrorNoVars("No assignable variables available")

        variable = self._instance.choose_variable(vars=self._vars, solution=curr_sol)

        for value in self._instance.get_values(
            var=variable,
            solution=curr_sol,
            pruned_vals=self._pruned_vals[hash(variable)],
        ):
            if not self._instance.is_feasible_value(
                val=value, var=variable, solution=curr_sol
            ):
                continue

            self._assigned_val_at_level[self._level] = (variable, value)
            self._vars.remove(variable)
            self._pruned_vals[hash(variable)].add(value)

            self._solution_at_level[self._level] = deepcopy(curr_sol)
            solution = self._instance.assign_value(
                val=value, var=variable, solution=curr_sol
            )

            self._level += 1
            self._curr_step += 1

            return solution

        if self._level == 0:
            self._set_up()
            raise ErrorCantFindSolution("Can't find a solution.")

        #### Backtrack
        # go one level up
        self._level -= 1

        # remove assigned value from domain
        previous_var, previous_val = self._assigned_val_at_level[self._level]
        self._pruned_vals[hash(previous_var)].add(previous_val)
        self._pruned_vals[hash(variable)].clear()
        self._vars.add(previous_var)

        # return solution one level above
        self._curr_step += 1
        return self._solution_at_level[self._level]
