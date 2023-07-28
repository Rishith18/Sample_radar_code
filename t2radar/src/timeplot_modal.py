from tkinter import *
from tkinter.ttk import *
from os import listdir
import processor.heatmap as hp
from gui.state import get_state
import lib.filter_utils as filters
import lib.file_utils as file_util
import lib.image_utils as image_util
import numpy as np

# A modal to edit the config
class TimePlotModal(object):

    def __init__(self, root: Tk, latest=False) -> None:

        if latest:
            file_name = self.getLatestFile()
            path = "./data/" + file_name
            print(path)
            data = file_util.read_data_file(path)
            data["data"] = np.log10(data["data"])
            # hp.generate_heatmap(data, "m")
            return

        self.root = Toplevel(root)
        self.root.grab_set()

        self.root.title("Generate Range-Time Plot")

        fileselect_title = Label(
            self.root, text="Select File", font=("Helvetica", 16))
        fileselect_title.pack()

        self.files = Variable(value=[])
        self.update_files()
        self.file_box = Listbox(self.root, height=20, width=70,
                                listvariable=self.files)
        self.file_box.pack()

        generate_button = Button(
            self.root, text="Generate", command=self.generate)
        generate_button.pack()

        generate_button = Button(
            self.root, text="Generate Filtered", command=self.generate_filtered)
        generate_button.pack()

    def update_files(self) -> None:
        files = listdir("./data")

        # only files ending in .pkl
        files = [f for f in files if f.endswith(".pkl")]

        self.files.set(files)

    def getLatestFile(self) -> str:
        files = listdir("./data")

        # only files ending in .pkl
        files = [f for f in files if f.endswith(".pkl")]

        # sort by name
        files.sort()

        return files[-1]

    def generate(self):

        # get unit preference
        unit = get_state("config")["ui"]["units"]

        # get file name
        file_name = self.file_box.get(self.file_box.curselection())

        # construct path
        path = "./data/" + file_name

        data = file_util.read_data_file(path)

        data["data"] = np.log10(data["data"])

        image_util.get_radar_start_time(data)

        # generate the plot
        # hp.generate_heatmap(data, unit)

    def generate_filtered(self):

        # get unit preference
        unit = get_state("config")["ui"]["units"]

        # get file name
        file_name = self.file_box.get(self.file_box.curselection())

        # construct path
        path = "./data/" + file_name

        data = file_util.read_data_file(path)
        filtered_data = filters.apply_log(data)
        filtered_data = filters.apply_log(data)

        # good results with value_threshold=40, count_threshold=4
        filtered_data = filters.iterative_denoise(
            filtered_data, value_threshold=40, count_threshold=3)

        filter_type = "gausian"
        # filter_threshold=0
        filtered_data = filters.apply_filter(
            radar_data=filtered_data, filter_name=filter_type, filter_threshold=0)

        # value_threshold=50, count_threshold=4
        filtered_data = filters.iterative_denoise(filtered_data, value_threshold=50, count_threshold=3)
        # print(filtered_data)

        # 50, 10, 65 worked well
        bucketized_data = filters.bucketize_radar_data(filtered_data, first_bucket_threshold=50, bucket_size=10, output_threshold=65)

        #correlation check
        move_time = image_util.get_radar_start_time(bucketized_data)
        move_time = image_util.get_radar_start_time(bucketized_data)

        # generate the plot
        hp.generate_heatmap(filtered_data, unit)
        hp.generate_heatmap(filtered_data, unit)
