from tkinter import ttk
import tkinter as tk

from app.optimization.algorithm_enum import Neighborhoods
from app.optimization.local_search.meta_heuristics.simulated_annealing import (
    CoolingSchedule,
)


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent.root)
        self.title("Settings")
        self.geometry("500x300")

        self.parent = parent

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.save_button = ttk.Button(self, text="save", command=self.save_settings)
        self.save_button.pack()

        self.create_sim_ann_tab()
        self.create_backtracking_tab()
        self.create_hill_climbing_tab()

    def save_settings(self) -> None:
        self.parent.settings_temperature = int(self.temp_entry.get())
        self.parent.settings_cooling_schedule = CoolingSchedule._value2member_map_[
            self.cooling_schedule.get()
        ]
        self.parent.settings_box_limit = int(self.box_limit.get())
        self.parent.neighborhoods = Neighborhoods._value2member_map_[
            self.neighborhoods.get()
        ]
        print(self.parent.neighborhoods)

        self.destroy()

    def create_sim_ann_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Simulated Annealing")

        ttk.Label(tab, text="Temperature:").grid(
            row=0, column=0, padx=10, pady=5, sticky=tk.W
        )
        self.temp_entry = ttk.Entry(tab)
        self.temp_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        self.temp_entry.insert(0, str(self.parent.settings_temperature))

        ttk.Label(tab, text="Cooling schedule:").grid(
            row=1, column=0, padx=10, pady=5, sticky=tk.W
        )
        self.cooling_schedule = ttk.Combobox(
            tab, values=[CoolingSchedule.LOG.value, CoolingSchedule.GEOMETRIC.value]
        )
        self.cooling_schedule.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        match self.parent.settings_cooling_schedule:
            case CoolingSchedule.LOG:
                self.cooling_schedule.current(0)
            case CoolingSchedule.GEOMETRIC:
                self.cooling_schedule.current(1)

    def create_backtracking_tab(self) -> None:
        # Create a frame for the "Appearance" tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Backtracking")

        ttk.Label(tab, text="Box limit:").grid(
            row=1, column=0, padx=10, pady=5, sticky=tk.W
        )
        self.box_limit = tk.Entry(tab, width=5)
        self.box_limit.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        self.box_limit.insert(0, "1000")

    def create_hill_climbing_tab(self) -> None:
        # Create a frame for the "Appearance" tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Neighborhood")

        ttk.Label(tab, text="Cooling schedule:").grid(
            row=1, column=0, padx=10, pady=5, sticky=tk.W
        )

        self.neighborhoods = ttk.Combobox(
            tab, values=[Neighborhoods.GEOMETRIC.value, Neighborhoods.RULE_BASED.value, Neighborhoods.RELAXED_GEOMETRIC.value]
        )
        self.neighborhoods.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        match self.parent.neighborhoods:
            case Neighborhoods.GEOMETRIC:
                self.neighborhoods.current(0)
            case Neighborhoods.RULE_BASED:
                self.neighborhoods.current(1)
            case Neighborhoods.RELAXED_GEOMETRIC:
                self.neighborhoods.current(2)
