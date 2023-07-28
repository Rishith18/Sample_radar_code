from collections import deque

# create the "./data" directory if it doesn't exist
import os
if not os.path.exists("./data"):
    os.makedirs("./data")


def save_data(data: deque, start_range: float, end_range: float, filepath: str):
    """ Saves the data to a file.
        Args:
            data (deque): A deque of data sets
            start_range (float): The start range of the scan (in meters)
            end_range (float): The end range of the scan (in meters)
            filepath (str): The path where to save the file 
        Returns:
            None
    """

    print("Saving to " + filepath)

    # construct the header
    point_count = len(data[0]["data"])

    range_delta = (end_range - start_range) / point_count

    header = f"{start_range},{end_range},{range_delta}\n"

    # write the data to the file
    with open(filepath, "w") as f:

        f.write(header)

        for element in data:
            timestamp = element["timestamp"]
            data_points = ",".join([str(x) for x in element["data"]])

            line = f"{timestamp}: {data_points}\n"

            f.write(line)

        f.close()

    return None
