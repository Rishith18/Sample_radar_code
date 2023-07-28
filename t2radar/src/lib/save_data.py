from collections import deque
import pickle

# create the "./data" directory if it doesn't exist
import os
if not os.path.exists("./data"):
    os.makedirs("./data")


def save_data(data: deque, start_range: float, end_range: float, file_path: str):
    """ Saves the data to a file.
        Args:
            data (deque): A deque of data sets
            start_range (float): The start range of the scan (in meters)
            end_range (float): The end range of the scan (in meters)
            filepath (str): The path where to save the file 
        Returns:
            None
    """

    print("Saving to " + file_path)

    # construct the header
    point_count = len(data[0]["data"])
    frame_count = len(data)

    header = {
        "point_count": point_count,
        "frame_count": frame_count,
        "start_range": start_range,
        "end_range": end_range
    }

    with open(file_path, 'wb') as f:
        # write the header
        pickle.dump(header, f)

        # write the data
        for frame in data:
            pickle.dump(frame, f)

        f.close()
    print("Done saving.")

    return None
