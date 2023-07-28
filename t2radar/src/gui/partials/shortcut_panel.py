from tkinter import *
from tkinter.ttk import *

from timeplot_modal import TimePlotModal


class ShortcutPanel(Frame):

    def __init__(self, root: Tk):
        Frame.__init__(self, root)

        self.root = root
        root = Frame(root)

        # label
        label = Label(root, text="Shortcuts", font=("Helvetica", 16))
        label.pack(side=TOP)

        # button for time plot modal
        timeplot_button = Button(root, text="Generate Range-Time Plot",
                                 command=lambda: TimePlotModal(self.root))
        timeplot_button.pack(side=TOP)

        # button to generate latest range-time plot
        latest_timeplot_button = Button(root, text="Generate Latest RT Plot",
                                        command=lambda: TimePlotModal(self.root, True))
        latest_timeplot_button.pack(side=TOP)

        root.pack(side=TOP)
