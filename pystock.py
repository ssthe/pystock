from tkinter import Tk

import gui as gui
from data import data

# Driver code
if __name__ == "__main__":
    data = data()
    master = gui.Main_window(data)
    master.mainloop()
