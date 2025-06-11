from tkinter import Tk
from app.gui.box_filling.box_filling_gui import BoxFillingApp


if __name__ == "__main__":
    root = Tk()
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
