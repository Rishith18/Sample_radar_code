from tkinter import *
from tkinter.ttk import *

from gui.partials.run_frame import RunFrame

from gui.partials.config_panel import ConfigPanel
from gui.partials.shortcut_panel import ShortcutPanel

from gui.partials.edit_config_modal import EditConfigModal


class MainWindow(object):

    def __init__(self, root: Tk):
        self.root = root
        """Displays the main window
        Args:
          root: Tk object
      """

        # set window to 800x600
        root.geometry("800x600")

        # set window title
        root.title("PulseON 440 Control Panel")

        # create a menu bar
        menubar = Menu(root)

        # create a config menu
        configmenu = Menu(menubar, tearoff=0)

        # add the config menu to the menu bar
        menubar.add_cascade(label="Configure", menu=configmenu)

        # add options to the config menu
        configmenu.add_command(label="Edit Config",
                               command=self.open_edit_config_modal)

        # add a menu to stop/start the radar
        radar_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Radar", menu=radar_menu)
        radar_menu.add_command(label="Start")
        radar_menu.add_command(label="Stop")

        # add the menu bar to the window
        root.config(menu=menubar)

        # create a frame to hold the status displays
        status_displays = Frame(root, border=1, relief="sunken")

        # create a config panel
        self.config_panel = ConfigPanel(status_displays)

        # add the shortcut panel
        self.shortcut_panel = ShortcutPanel(status_displays)

        # add a button to edit the config
        edit_config_button = Button(
            self.shortcut_panel.root, text="Edit Config", command=self.open_edit_config_modal)
        edit_config_button.pack()

        # fill y axis
        status_displays.pack(fill=Y, side=LEFT)

        # run frame fills the rest of the window
        RunFrame(root, self.update_all_status)

    def open_edit_config_modal(self):
        config = EditConfigModal(self.root)
        config.bindDeath(self.config_panel.update_status)

    def update_all_status(self):
        self.config_panel.update_status()
