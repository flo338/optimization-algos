from optimization.local_search.meta_heuristics.hill_climbing import HillClimbing
from optimization.local_search.meta_heuristics.simulated_annealing import (
    SimulatedAnnealing,
)
from problems.scheduling.instance import LocalSearchInstance

# Task scheduling
# Given a set of tasks with fixed durations and a set of workers with limited capacity, the optimization goal is to
# assign each task to a worker such that the overall workload is balanced and no worker exceeds his capacity.

task_durations = [1, 2, 3, 4, 4, 6, 7, 4, 4, 3, 6, 9]
num_workers = 10
max_load = 9

instance_for_simulated_annealing = LocalSearchInstance(
    task_durations, num_workers, max_load, meta_heuristic="Simulated Annealing"
)
instance_for_hill_climbing = LocalSearchInstance(
    task_durations, num_workers, max_load, meta_heuristic="Hill Climbing"
)
initial_solution = instance_for_simulated_annealing.generate_feasible_solution()

simulated_annealing = SimulatedAnnealing(instance_for_simulated_annealing, steps=100, temperature=1e6)
hill_climbing = HillClimbing(instance_for_simulated_annealing, steps=100)

sol_simulated_annealing = simulated_annealing.search(initial_solution)
sol_hill_climbing = hill_climbing.search(initial_solution)

score_initial = instance_for_simulated_annealing.obj([initial_solution])
score_simulated_annealing = instance_for_simulated_annealing.obj([sol_simulated_annealing])
score_hill_climbing = instance_for_hill_climbing.obj([sol_hill_climbing])
score_init = instance_for_simulated_annealing.obj([initial_solution])

print(f"Simulated Annealing: {sol_simulated_annealing.solution}\n{score_init[0]:.2f} -> {score_simulated_annealing[0]:.2f} +{abs(score_initial[0]-score_simulated_annealing[0]):.2f}")
print("\n")
print(f"Hill Climbing: {sol_hill_climbing.solution}\n{score_init[0]:.2f} -> {score_hill_climbing[0]:.2f}  +{abs(score_initial[0]-score_hill_climbing[0]):.2f}")
