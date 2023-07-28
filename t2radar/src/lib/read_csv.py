import pandas
import numpy as np


def read_csv(filepath: str, object_name: str) -> np.ndarray:
    """
    filepath: path to csv file

    """

    # read in csv
    df = pandas.read_csv(filepath, header=[2, 4, 5])

    # extracts time info
    times = df["Name"].to_numpy()
    if (object_name == "time"):
        return times

    info = df[object_name].to_numpy()

    # removes unnecessary columns
    info = np.delete(info, [0, 1, 3, 7], axis=1)

    # FIXME: Swaps y and z coordinates. May need to delete if not needed
    info[:, [3, 2]] = info[:, [2, 3]]

    return np.hstack((times, info))


def slice_csv(rawdata, start_frame, end_frame):
    """
    rawdata: data from read_csv
    start_frame: frame to start at
    end_frame: frame to end at
    """
    return rawdata[start_frame:end_frame, :]
