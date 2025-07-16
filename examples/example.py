"""
Given a set of tasks with fixed durations and a set of workers with limited capacity, the optimization goal is to 
assign each task to a worker such that the overall workload is balanced and no worker exceeds his capacity.
"""

from optimization.local_search.meta_heuristics.simulated_annealing import SimulatedAnnealing
from problems.scheduling.instance import TaskSchedulingInstance

task_durations = [1,2,3,4,4,6,7,4,4,3,6,9]
num_workers = 10
max_load = 9

instance = TaskSchedulingInstance(task_durations, num_workers, max_load)
initial_solution = instance.generate_feasible_solution()
local_search = SimulatedAnnealing(instance, steps=100, temperature=1e6)
new_sol = local_search.search(initial_solution)


print(f"Initial solution: {initial_solution}")
print(f"Initial score: {(init_score:=instance.obj([initial_solution]))}")
print("\n")
print(f"Final solution: {new_sol}")
print(f"Final score: {(final_score:=instance.obj([new_sol]))}")
print(f"\nImprovement -> +{final_score[0]-init_score[0]}")
