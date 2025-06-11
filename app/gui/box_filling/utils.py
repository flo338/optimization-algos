from tkinter.scrolledtext import ScrolledText
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import tkinter as tk


def get_custom_cmap():
    # Specify the color for 0
    zero_color = "white"  # You can change this to whatever color you want

    # Use the 'coolwarm' colormap (or any other colormap you prefer)
    cmap = plt.cm.get_cmap("hsv")

    # Define the new colors: start with the color for 0, then the rest of the colormap
    colors = [zero_color] + list(cmap(np.linspace(0, 1, cmap.N - 1)))

    # Create a new ListedColormap from the custom colors
    return mcolors.ListedColormap(colors)


def stopping_criterion(results: np.ndarray, threshold: float) -> bool:
    return bool(np.std(results) < threshold)


def insert_text(text_box: ScrolledText, text: str):
    text_box.config(state="normal")
    text_box.insert(
        index=tk.END,
        chars=text,
    )  # type: ignore
    text_box.see(tk.END)
    text_box.config(state="disabled")
