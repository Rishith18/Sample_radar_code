from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import showerror
from gui.state import get_state, set_state
from lib.util import range_to_ps, ps_to_range
from lib.config import write_config_file

# A modal to edit the config


class EditConfigModal(object):

    def __init__(self, root: Tk) -> None:
        self.root = Toplevel(root)
        self.root.grab_set()

        self.root.title("Edit Config")

        self.txt_ip = StringVar()
        self.txt_port = StringVar()

        self.txt_intindex = StringVar()
        self.scan_start = StringVar()
        self.scan_end = StringVar()
        self.scan_interval = StringVar()
        self.scan_count = StringVar()
        self.distance_correction = StringVar()

        self.display_units = StringVar()

        # input for IP
        ip_label = Label(self.root, text="IP")
        ip_label.grid(row=0, column=0)
        ip_input = Entry(self.root, textvariable=self.txt_ip)

        # input for port
        port_label = Label(self.root, text="Port")
        port_label.grid(row=1, column=0)
        port_input = Entry(self.root, textvariable=self.txt_port)

        # input for intindex
        intindex_label = Label(self.root, text="Integration")
        intindex_label.grid(row=2, column=0)
        intindex_input = Entry(self.root, textvariable=self.txt_intindex)

        # input for scan start
        scan_start_label = Label(self.root, text="Scan Start (m)")
        scan_start_label.grid(row=3, column=0)
        scan_start_input = Entry(self.root, textvariable=self.scan_start)

        # input for scan end
        scan_end_label = Label(self.root, text="Scan End (m)")
        scan_end_label.grid(row=4, column=0)
        scan_end_input = Entry(self.root, textvariable=self.scan_end)

        # input for scan interval
        scan_interval_label = Label(self.root, text="Scan Interval (m)")
        scan_interval_label.grid(row=5, column=0)
        scan_interval_input = Entry(self.root, textvariable=self.scan_interval)

        # input for scan count
        scan_count_label = Label(self.root, text="Scan Count")
        scan_count_label.grid(row=6, column=0)
        scan_count_input = Entry(self.root, textvariable=self.scan_count)

        # input for distance correction
        distance_correction_label = Label(
            self.root, text="Distance Correction")
        distance_correction_label.grid(row=7, column=0)
        distance_correction_input = Entry(
            self.root, textvariable=self.distance_correction)

        # input for unit selection (ft/m)
        display_unit_label = Label(
            self.root, text="Display Units")
        display_unit_label.grid(row=8, column=0)

        # use radio
        display_unit_radio = Frame(self.root)
        display_unit_radio.grid(row=8, column=1)

        display_unit_radio_ft = Radiobutton(
            display_unit_radio, text="ft", variable=self.display_units, value="ft")
        display_unit_radio_ft.pack(side=LEFT)

        display_unit_radio_m = Radiobutton(
            display_unit_radio, text="m", variable=self.display_units, value="m")
        display_unit_radio_m.pack(side=LEFT)

        # update button
        update_button = Button(self.root, text="Update",
                               command=self.update_config)

        # pack inputs
        ip_input.grid(row=0, column=1)
        port_input.grid(row=1, column=1)
        intindex_input.grid(row=2, column=1)
        scan_start_input.grid(row=3, column=1)
        scan_end_input.grid(row=4, column=1)
        scan_interval_input.grid(row=5, column=1)
        scan_count_input.grid(row=6, column=1)
        distance_correction_input.grid(row=7, column=1)
        display_unit_radio.grid(row=8, column=1)
        update_button.grid(row=9, column=1)

        self.update_status()

        # initialize the values
        stat = get_state("config")

        self.txt_ip.set(stat["net"]["ip"])
        self.txt_port.set(stat["net"]["port"])

        self.txt_intindex.set(stat["radar"]["integrationIndex"])
        self.scan_start.set(ps_to_range(stat["radar"]["scanStart"]))
        self.scan_end.set(ps_to_range(stat["radar"]["scanEnd"]))
        self.scan_interval.set(stat["radar"]["scanInterval"])
        self.scan_count.set(stat["radar"]["scanCount"])
        self.distance_correction.set(stat["radar"]["distanceCorrection"])

        # set the death callback
        self.deathCallback = lambda: None

    def update_status(self):
        """Updates the values in the modal"""

        config = get_state("config")

        net_cfg = config["net"]

        self.txt_ip.set(net_cfg["ip"])
        self.txt_port.set(net_cfg["port"])

        radar_cfg = config["radar"]

        self.txt_intindex.set(radar_cfg["integrationIndex"])

        self.scan_start.set(ps_to_range(radar_cfg["scanStart"]))
        self.scan_end.set(ps_to_range(radar_cfg["scanEnd"]))

        self.scan_interval.set(radar_cfg["scanInterval"])

        # if scan count is 65535, then it is infinite
        self.scan_count.set(radar_cfg["scanCount"]
                            if radar_cfg["scanCount"] != 65535 else 0)

        self.distance_correction.set(radar_cfg["distanceCorrection"])

        self.display_units.set(config["ui"]["units"])

    def update_config(self):
        """Updates the config"""

        config = get_state("config")

        try:
            config["net"]["ip"] = self.txt_ip.get()
            config["net"]["port"] = int(self.txt_port.get())

            config["radar"]["integrationIndex"] = int(self.txt_intindex.get())
            config["radar"]["scanStart"] = range_to_ps(
                float(self.scan_start.get()))
            config["radar"]["scanEnd"] = range_to_ps(
                float(self.scan_end.get()))

            config["radar"]["scanInterval"] = int(self.scan_interval.get())
            config["radar"]["scanCount"] = int(self.scan_count.get())
            config["radar"]["scanCount"] = 65535 if config["radar"]["scanCount"] == 0 else config["radar"]["scanCount"]
            config["radar"]["distanceCorrection"] = float(
                self.distance_correction.get())

            config["ui"]["units"] = self.display_units.get()

        except ValueError:
            # throw up a modal
            showerror("Error", "Invalid input")
            return

        # update the config
        set_state("config", config)

        # write the config
        write_config_file(config)

        self.deathCallback()

        # kill the modal
        self.root.destroy()

    def bindDeath(self, callback):
        """Binds a callback to when the modal is destroyed"""

        self.deathCallback = callback
