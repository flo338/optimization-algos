from abc import abstractmethod
from tkinter import Tk
import typing

from app.optimization.solution import ProblemSolution


class Gui(typing.Protocol):
    root: Tk

    @abstractmethod
    def __init__(self, root: Tk):
        self.root = root

    @abstractmethod
    def visualization_step(self, solution: ProblemSolution) -> None:
        """
        Visualizes the solution.
        """
        raise NotImplementedError


def get_curr_screen_geometry():
    """
    (Copied from stack overflow)

    Workaround to get the size of the current screen in a multi-screen setup.

    Returns:
        geometry (str): The standard Tk geometry string.
            [width]x[height]+[left]+[top]
    """
    root = Tk()
    root.update_idletasks()
    root.attributes("-fullscreen", True)
    root.state("iconic")
    height = root.winfo_height()
    width = root.winfo_width()
    root.destroy()
    return height, width
