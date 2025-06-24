To setup your environment run `bash setup.sh` from the base directory.
Afterwards you only need to activate the virtual environment via `source venv/bin/activate`.

# Contents
The repository offers an educational framework for a few optimization algorithms.
Including a general implementation of _backtracking_ aswell as a base class for _local search_ algorithms. The repository includes Hill Climbing, aswell as Simulated Annealing as meta heuristics of the _local search_ algorithm.

In order to use the the optimization algorithms, you need to implement the following protocols: ProblemSolution, Objective, Neighborhood (for the local search) and a ProblemInstance which orchestrates the individual parts.
This design allows for playing around with different neighborhoods and objective functions easily.
An example implementation is provided for the box filling problem, where the objective lays in using the smallest amount of fixed size boxes, to store a set of rectangles.
All optimization algorithms can be run until some termination criterion or step by step.

**Example usage**:
```
problem_instance = YourProblemInstance()
search_algorithm = SimulatedAnnealing(problem_instsance=problem_instance, steps=1000)
```

Either search step by step
```
solution = problem_instance.generate_feasible_solution()
new_solution = search_algorithm.step(solution)
```
or search until convergance
```
final_solution = search_algorithm.search()
```

NOTE: The repository mainly serves for getting to know the algorithms better, hence the the implementations are not the most efficient.
