import argparse
import time

import numpy as np
from app.gui.box_filling.box_filling_gui import ATTEMPTS
from app.gui.box_filling.utils import stopping_criterion
from app.optimization.algorithm_enum import Algorithm
from app.optimization.backtracking.backtracking import Backtracking
from app.optimization.local_search.meta_heuristics.hill_climbing import HillClimbing
from app.optimization.local_search.meta_heuristics.simulated_annealing import (
    CoolingSchedule,
    SimulatedAnnealing,
)
from app.problems.box_filling.instance import BoxFilling, BoxFillingFactory
from app.problems.box_filling.local_search.objectives import POWER
from app.problems.box_filling.solution import BoxFillingSolution


STEPS = 10_000


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b", "--box_size", type=int, help="The Edge length of the boxes", default=20
    )
    parser.add_argument(
        "-minw", "--min_width", type=int, help="Minimum width of rectangles", default=1
    )
    parser.add_argument(
        "-maxw", "--max_width", type=int, help="Maximum width of rectangles", default=10
    )
    parser.add_argument(
        "-minh",
        "--min_height",
        type=int,
        help="Minimum height of rectangles",
        default=1,
    )
    parser.add_argument(
        "-maxh",
        "--max_height",
        type=int,
        help="Maximum height of rectangles",
        default=10,
    )
    parser.add_argument(
        "-rectnb",
        "--rectangle_number",
        type=int,
        help="Number of rectangles",
        default=100,
    )
    parser.add_argument(
        "-a",
        "--algorithm",
        type=Algorithm,
        help="Name of the algorithm",
        default=Algorithm.SIMULATED_ANNEALING,
    )
    parser.add_argument(
        "-t", "--temperature", type=float, help="Temperature", default=50
    )
    parser.add_argument(
        "-cs",
        "--cooling_schedule",
        type=CoolingSchedule,
        help="Cooling schedule",
        default=CoolingSchedule.GEOMETRIC,
    )

    return parser.parse_args()


if __name__ == "__main__":
    bff = BoxFillingFactory()

    args = parse_args()

    instance: BoxFilling = bff.get_instance(
        L=args.box_size,
        rect_num=args.rectangle_number,
        max_width=args.max_width,
        min_width=args.min_width,
        max_height=args.max_height,
        min_height=args.min_height,
    )
    s_star: BoxFillingSolution = instance.generate_feasible_solution()

    selected_searcher = args.algorithm
    match selected_searcher:
        case Algorithm.HILL_CLIMBING:
            searcher = HillClimbing(instance=instance, steps=STEPS)
        case Algorithm.SIMULATED_ANNEALING:
            searcher = SimulatedAnnealing(
                instance=instance,
                steps=STEPS,
                temperature=args.temperature,
                C=args.rectangle_number**POWER,
                cooling_schedule=args.cooling_schedule,
            )
        case Algorithm.BACKTRACKING:
            searcher = Backtracking(
                instance=instance, steps=STEPS, vars=set(s_star.solution)
            )
            s_star.solution = []

    objv = instance.obj(solution=[s_star])[0]
    results = np.random.normal(0, scale=10, size=ATTEMPTS)
    box_nb_start = len(set([rect.box for rect in s_star.solution]))

    print("# Run started")
    print(f"## start objective value: {objv:.2f}")
    print(f"## initial boxes used: {box_nb_start}")
    print("-"*40)
    print("\n")

    start_time = time.time()

    for step in range(STEPS):

        try:
            s_star = searcher.step(curr_sol=s_star)  # type: ignore
            s_star.reduce_boxes()

            if selected_searcher != Algorithm.BACKTRACKING:
                curr_obj = instance.obj([s_star])[0]
                results[step % ATTEMPTS] = curr_obj

                if stopping_criterion(results=results, threshold=1e-5):
                    solution = s_star
                    break

        except Exception:
            solution = s_star
            break

    end_time = time.time()

    objv = instance.obj(solution=[solution])[0]
    box_nb_end = len(set([rect.box for rect in s_star.solution]))
    print("# Run completed")
    print(f"## end objective value: {objv:.2f}")
    print(f"## final boxes used: {box_nb_end}")
    print(f"## time elapsed: {(end_time-start_time):.2f} s")
    print("-"*40)
    print("\n")
    print("Run specifications:")
    for key, value in vars(args).items():
        print(f"\t{key}: {value}")
    print("-" * 40)
