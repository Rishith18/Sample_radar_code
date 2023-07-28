import os
import numpy as np
import pickle


def read_data_file(filePath):
    """Reads the provided file.

        Args:
            filePath (string): Full path to data file.
        Returns:
            dictionary with keys: data (numpy array), time (list), start (float), end (float);
            dictionary with keys: data (numpy array), time (list), start (float), end (float);
    """

    file_exists = os.path.isfile(filePath)

    if file_exists == True:

        time = np.array([])
        data = np.array([])

        # read the pickle files
        with open(filePath, "rb") as f:
            header = pickle.load(f)

            start = header["start_range"]
            end = header["end_range"]
            point_count = header["point_count"]
            frame_count = header["frame_count"]

            # read the data
            for i in range(frame_count):
                frame = pickle.load(f)
                time = np.append(time, frame["timestamp"])
                data = np.append(data, frame["data"])

            f.close()

        data = np.reshape(data, (frame_count, point_count))

        data = np.abs(data)

        # set minimum value to 1e-8
        data[data < 1e-8] = 1e-8

        return {
            "data": data,
            "time": time,
            "start": start,
            "end": end
        }
    else:
        return {
            "data": np.array([]),
            "time": [],
            "start": 0.0,
            "end": 0.0
        }
