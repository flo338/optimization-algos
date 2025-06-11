import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import matplotlib
from matplotlib.axes import Axes
import matplotlib.figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from app.gui.base_gui import Gui
from app.gui.box_filling.settings_window import SettingsWindow
from app.gui.box_filling.utils import get_custom_cmap, insert_text, stopping_criterion
from app.optimization.algorithm_enum import Algorithm, Neighborhoods
from app.optimization.backtracking.backtracking import Backtracking
from app.optimization.exceptions import ErrorNoVars
from app.optimization.local_search.instance import ProblemInstance
from app.optimization.local_search.local_search import ErrorNoImprovement
from app.optimization.local_search.meta_heuristics.hill_climbing import HillClimbing
from app.optimization.local_search.meta_heuristics.simulated_annealing import (
    CoolingSchedule,
    SimulatedAnnealing,
)
from app.optimization.solution import ProblemSolution
from app.problems.box_filling.instance import BoxFillingFactory
from app.problems.box_filling.local_search.neighborhoods.relaxed_geometric_neighborhood import BoxFillingInstanceRelaxedGeometric, BoxFillingSolutionRelaxedGeometric, build_box
from app.problems.box_filling.local_search.neighborhoods.rule_based import BoxFillingInstanceRuleBased, BoxFillingSolutionRuleBased, approx_needed_boxes, place_permutation_row_first
from app.problems.box_filling.local_search.objectives import POWER
from app.problems.box_filling.solution import BoxFillingSolution

matplotlib.use("TkAgg")
custom_cmap = get_custom_cmap()

ATTEMPTS = 10000#int((50*49)/2)
THRESHOLD = 0


class BoxFillingApp(Gui):
    def __init__(self, root: tk.Tk):
        # Define variables
        super().__init__(root=root)

        self.box_num: int
        self.box_size: int
        self.axes: list[Axes] = []
        self.active_grid: bool = False
        self.stop_search_ = False

        # Settings window
        self.settings_temperature: int = 0
        self.settings_cooling_schedule: CoolingSchedule = CoolingSchedule.LOG
        self.settings_box_limit: int = 1000
        self.neighborhoods: Neighborhoods = Neighborhoods.GEOMETRIC

        # Declare variables
        self.figure: matplotlib.figure.Figure
        self.scatter: FigureCanvasTkAgg
        self.grids: list[np.ndarray]

        # Control frame
        self.control_frame = tk.Frame(root, width=15)
        self.control_frame.pack(
            side="left",
            anchor="nw",
            fill="y",
        )
        self.plot_area_init = tk.Canvas(self.root, bg="white")
        self.plot_area_init.pack(side="right", fill="both", expand=True)

        # Box size config
        self.box_size_input = tk.Label(
            self.control_frame, text="Box size:", font=("TkDefaultFont", 13, "bold")
        )
        self.box_size_input.grid(row=0, column=0, sticky="nw")
        self.box_size_entry = tk.Entry(self.control_frame, width=5)
        self.box_size_entry.grid(row=0, column=1, sticky="ne")
        self.box_size_entry.insert(0, "20")

        # Rectangle width config
        self.width = tk.Label(
            self.control_frame, text="Width", font=("TkDefaultFont", 13, "bold")
        )
        self.width.grid(row=1, column=0, sticky="nw")

        self.min_width = tk.Label(self.control_frame, text="min:")
        self.min_width.grid(row=2, column=0, sticky="nw")
        self.min_width_entry = tk.Entry(self.control_frame, width=5)
        self.min_width_entry.grid(row=2, column=1, sticky="ne")
        self.min_width_entry.insert(0, "1")

        self.max_width = tk.Label(self.control_frame, text="max:")
        self.max_width.grid(row=3, column=0, sticky="nw")
        self.max_width_entry = tk.Entry(self.control_frame, width=5)
        self.max_width_entry.grid(row=3, column=1, sticky="ne")
        self.max_width_entry.insert(0, "10")

        # Rectangle height config
        self.width = tk.Label(
            self.control_frame, text="Height", font=("TkDefaultFont", 13, "bold")
        )
        self.width.grid(row=4, column=0, sticky="nw")

        self.min_height = tk.Label(self.control_frame, text="min:")
        self.min_height.grid(row=5, column=0, sticky="nw")
        self.min_height_entry = tk.Entry(self.control_frame, width=5)
        self.min_height_entry.grid(row=5, column=1, sticky="ne")
        self.min_height_entry.insert(0, "1")

        self.max_height = tk.Label(self.control_frame, text="max:")
        self.max_height.grid(row=6, column=0, sticky="nw")
        self.max_height_entry = tk.Entry(self.control_frame, width=5)
        self.max_height_entry.grid(row=6, column=1, sticky="ne")
        self.max_height_entry.insert(0, "10")

        # Rectangle number config
        self.rect_num = tk.Label(self.control_frame, text="Rect. Num.: ")
        self.rect_num.grid(row=7, column=0, sticky="nw")
        self.rect_num_entry = tk.Entry(self.control_frame, width=5)
        self.rect_num_entry.grid(row=7, column=1, sticky="ne")
        self.rect_num_entry.insert(0, "50")

        # Algorithm selection config
        self.searcher = tk.StringVar()
        self.searcher.set("Simulated Annealing")
        self.option_menu = tk.OptionMenu(
            self.control_frame,
            self.searcher,
            "Simulated Annealing",
            "Hill Climbing",
            "Backtracking",
        )
        self.option_menu.grid(row=8, columnspan=2, sticky="nw")

        # Settings
        self.settings_button = tk.Button(
            self.control_frame, text="Settings", command=self.open_settings
        )
        self.settings_button.grid(row=12, sticky="sw")

        # Visualization steps
        self.step_scheme = tk.StringVar()
        self.step_scheme.set("removed box")
        self.step_scheme_option_menu = tk.OptionMenu(
            self.control_frame,
            self.step_scheme,
            "removed box",
            "every 1",
            "every 20",
            "every 50",
            "every 100",
            "every 500",
            "every 1000",
            "End Result",
        )
        self.step_scheme_option_menu.grid(row=9, columnspan=2, sticky="nw")

        # Run button config
        self.run_button = tk.Button(
            self.control_frame, text="Run search", command=self.run
        )
        self.run_button.grid(row=10, column=0, columnspan=1, sticky="nw")

        # stop button config
        self.stop_button = tk.Button(
            self.control_frame, text="stop", command=self.stop_search
        )
        self.stop_button.grid(row=10, column=1, columnspan=1, sticky="nw")

        # Info area config
        self.info = ScrolledText(self.control_frame, width=20, height=15)
        self.info.grid(row=11, columnspan=2)
        self.info.config(state="disabled")

    def stop_search(self):
        self.stop_search_ = True
        return

    def init_grid(self, box_num: int):
        if self.active_grid:
            self.scatter.get_tk_widget().destroy()
            plt.close(self.figure)
        else:
            self.plot_area_init.destroy()
            self.active_grid = True

        self.box_size = int(self.box_size_entry.get())

        self.figure_measure = np.ceil(np.sqrt(box_num))
        self.figure = plt.figure(
            figsize=(self.figure_measure * 2, self.figure_measure * 2)
        )
        self.scatter = FigureCanvasTkAgg(self.figure, self.root)
        self.scatter.get_tk_widget().pack(side="right", fill="both", expand=True)
        self.axes = []

        self.grids = [
            np.zeros((self.box_size, self.box_size), dtype=int) for _ in range(box_num)
        ]

        for i in range(box_num):
            ax = self.figure.add_subplot(
                int(self.figure_measure), int(self.figure_measure), i + 1
            )
            ax.pcolormesh(self.grids[i], linewidth=0, cmap=custom_cmap)
            ax.invert_yaxis()
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
            ax.set_aspect("equal")
            self.axes.append(ax)

    def visualization_step(self, solution: BoxFillingSolution | BoxFillingSolutionRuleBased | BoxFillingSolutionRelaxedGeometric) -> None:
        if isinstance(solution, BoxFillingSolutionRuleBased):
            grids = [grid for grid in place_permutation_row_first(permutation=solution.solution, box_size=solution.box_size) if grid.any()]
            self.init_grid(len(grids))
            self.grids = grids
        elif isinstance(solution, BoxFillingSolution):            
            # Initialize empty grids (boxes)
            self.grids = [
                np.zeros((self.box_size, self.box_size), dtype=int)
                for _ in range(len(self.axes))
            ]

            # Fill the grids
            for rect in solution.solution:
                for coords in rect.coordinates:
                    self.grids[coords[0]][coords[1], coords[2]] = rect.index
        elif isinstance(solution, BoxFillingSolutionRelaxedGeometric):
            grids = [grid for grid in build_box(solution=solution.solution, L=self.box_size, needed_boxes=approx_needed_boxes(solution.solution[:,[2,3,5]], box_size=self.box_size)) if grid.any()]
            self.init_grid(len(grids))
            self.grids = grids

        for i in range(len(self.axes)):
            self.axes[i].clear()
            self.axes[i].pcolormesh(
                self.grids[i], edgecolors="k", linewidth=0, cmap=custom_cmap
            )
            self.axes[i].invert_yaxis()
            self.axes[i].set_aspect("equal")

        self.scatter.draw()

    @staticmethod
    def visualization_scheduler(step: int, new_box: bool, mode: str):
        match mode:
            case "removed box":
                return new_box
            case "every 1":
                return True
            case "every 20":
                return step % 20 == 0
            case "every 50":
                return step % 50 == 0
            case "every 100":
                return step % 100 == 0
            case "every 500":
                return step % 500 == 0       
            case "every 1000":
                return step % 1000 == 0                    
            case "End Result":
                return False

    def open_settings(self):
        SettingsWindow(parent=self)

    def run(self) -> None:
        bff = BoxFillingFactory()

        box_size = int(self.box_size_entry.get())
        max_width = int(self.max_width_entry.get())
        min_width = int(self.min_width_entry.get())
        max_height = int(self.max_height_entry.get())
        min_height = int(self.min_height_entry.get())
        rect_num = int(self.rect_num_entry.get())
        vis_mode = self.step_scheme.get()
        steps = 100000

        # Get Box filling instance
        instance: ProblemInstance = bff.get_instance(
            L=box_size,
            rect_num=rect_num,
            max_width=max_width,
            min_width=min_width,
            max_height=max_height,
            min_height=min_height,
            box_limit=self.settings_box_limit,
        )

        # Generate starting solution and setup results queue
        s_star: ProblemSolution = instance.generate_feasible_solution()
        results = np.random.normal(0, scale=10, size=ATTEMPTS)

        # Initialize boxes
        self.box_num = max(rect.box for rect in s_star.solution) + 1
        self.init_grid(self.box_num)

        # Get selected searcher
        selected_searcher = self.searcher.get()
        match selected_searcher:
            case Algorithm.HILL_CLIMBING:
                nh = self.neighborhoods
                match nh:
                    case Neighborhoods.RULE_BASED:
                        instance = BoxFillingInstanceRuleBased(
                            L=box_size, rect_num=rect_num, max_width=max_width, max_height=max_height, min_width=min_width, min_height=min_height
                        )
                        s_star = instance.generate_feasible_solution()
                        self.box_num = approx_needed_boxes(s_star.solution, box_size=box_size)
                        self.init_grid(self.box_num)
                    
                    case Neighborhoods.RELAXED_GEOMETRIC:
                        instance = BoxFillingInstanceRelaxedGeometric(
                            L=box_size, rect_num=rect_num, max_width=max_width, max_height=max_height, min_width=min_width, min_height=min_height
                        )
                        s_star = instance.generate_feasible_solution()
                        self.box_num = approx_needed_boxes(s_star.solution[:,[2,3,5]], box_size=box_size)
                        self.init_grid(self.box_num)                        
                searcher = HillClimbing(instance=instance, steps=steps)
                searcher._attempts = ATTEMPTS

            case Algorithm.SIMULATED_ANNEALING:
                searcher = SimulatedAnnealing(
                    instance=instance,
                    steps=steps,
                    temperature=self.settings_temperature,
                    C=rect_num**POWER,
                    cooling_schedule=self.settings_cooling_schedule,
                )
            case Algorithm.BACKTRACKING:
                searcher = Backtracking(
                    instance=instance, steps=steps, vars=set(s_star.solution)
                )
                s_star.solution = []

        for step in range(steps):
            # Check if user stops search
            if self.stop_search_:
                insert_text(
                    text_box=self.info,
                    text="Search interrupted",
                )
                self.visualization_step(solution=s_star)  # type: ignore
                self.root.update()
                self.stop_search_ = False
                return

            # Update results queue
            curr_obj = instance.obj([s_star])[0]
            results[step % ATTEMPTS] = curr_obj

            # Check if objective function is increasing
            if (
                stopping_criterion(results=results, threshold=THRESHOLD)
                and not selected_searcher == Algorithm.BACKTRACKING
            ):
                insert_text(
                    text_box=self.info,
                    text=f"obj changed on average less that 1e-5 during the last {ATTEMPTS} iterations",
                )
                self.visualization_step(solution=s_star)  # type: ignore
                self.root.update()
                return

            # Check if visualization is required
            new_box_num = (
                max(rect.box for rect in s_star.solution) + 1 if isinstance(s_star, BoxFillingSolution) and selected_searcher != Algorithm.BACKTRACKING else 0
            )
            if self.visualization_scheduler(
                step=step, new_box=self.box_num != new_box_num, mode=vis_mode
            ):
                self.box_num = new_box_num
                self.visualization_step(solution=s_star)  # type: ignore
                insert_text(
                    text_box=self.info,
                    text=searcher.get_current_info(curr_obj=curr_obj),
                )
                self.root.update()

            try:
                # Make search step
                s_star = searcher.step(curr_sol=s_star)

                # Reduce boxes
                if isinstance(s_star, BoxFillingSolution):
                    s_star.reduce_boxes()
            except ErrorNoImprovement:
                insert_text(text_box=self.info, text="No Improvement")
                self.visualization_step(solution=s_star)
                self.root.update()
                return
            except ErrorNoVars:
                insert_text(text_box=self.info, text="No Variables available")
                self.visualization_step(solution=s_star)
                self.root.update()
                return

        insert_text(text_box=self.info, text="Steps exhausted")
        self.visualization_step(solution=s_star)
        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()
    root.geometry(f"{int(width//1.3)}x{int(height//1.3)}")
    root.resizable(False, False)

    def _quit():
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _quit)

    app = BoxFillingApp(root)
    root.mainloop()
