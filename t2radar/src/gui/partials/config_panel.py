from tkinter import *
from tkinter.ttk import *
from gui.state import get_state
from lib.util import ps_to_range
from gui.util import format_float


class ConfigPanel(Frame):

    def __init__(self, root: Tk):
        Frame.__init__(self, root)

        self.txt_ip = StringVar()
        self.txt_port = StringVar()

        self.txt_intindex = StringVar()
        self.scan_start = StringVar()
        self.scan_end = StringVar()
        self.scan_interval = StringVar()
        self.scan_count = StringVar()
        self.distance_correction = StringVar()
        self.display_units = StringVar()

        root = Frame(root)
        self.update_status()

        # title
        title = Label(root, text="Config", font=("Helvetica", 16))
        title.pack()

        # create labels
        ip_label = Label(root, textvariable=self.txt_ip)
        port_label = Label(root, textvariable=self.txt_port)

        intindex_label = Label(root, textvariable=self.txt_intindex)
        scan_start_label = Label(root, textvariable=self.scan_start)
        scan_end_label = Label(root, textvariable=self.scan_end)
        scan_interval_label = Label(root, textvariable=self.scan_interval)
        scan_count_label = Label(root, textvariable=self.scan_count)
        distance_correction_label = Label(
            root, textvariable=self.distance_correction)

        display_unit_label = Label(
            root, textvariable=self.display_units)

        # pack labels
        ip_label.pack()
        port_label.pack()

        intindex_label.pack()
        scan_start_label.pack()
        scan_end_label.pack()
        scan_interval_label.pack()
        scan_count_label.pack()
        distance_correction_label.pack()

        display_unit_label.pack()

        root.pack(side=TOP)

    def update_status(self):
        """Updates the status panel"""

        config = get_state("config")

        net_cfg = config["net"]

        self.txt_ip.set("IP: " + net_cfg["ip"])
        self.txt_port.set("Port: " + str(net_cfg["port"]))

        radar_cfg = config["radar"]

        self.txt_intindex.set(
            "Integration: " + str(radar_cfg["integrationIndex"]))

        start_dist = format_float(ps_to_range(radar_cfg["scanStart"]))
        end_dist = format_float(ps_to_range(radar_cfg["scanEnd"]))

        self.scan_start.set("Scan Start: " + str(start_dist) + "m")
        self.scan_end.set("Scan End: " + str(end_dist) + "m")

        self.scan_interval.set("Scan Interval: " +
                               str(radar_cfg["scanInterval"]))

        # if scan count is 65535, then it is infinite
        if radar_cfg["scanCount"] == 65535:
            self.scan_count.set("Scan Count: Infinite")
        else:
            self.scan_count.set("Scan Count: " + str(radar_cfg["scanCount"]))

        self.distance_correction.set(
            "Distance Correction: " + str(radar_cfg["distanceCorrection"]))

        self.display_units.set("Display Units: " + config["ui"]["units"])
