import numpy as np


def interpolate_mocap_frames(mocap_data: np.ndarray, radar_timestamps: np.ndarray, time_delta=0) -> np.ndarray:
    """Interpolates the motion capture data to match the radar timestamps.

      Args:
        mocap_data (np.ndarray): Motion capture data.
        radar_timestamps (np.ndarray): Radar timestamps.
        time_delta (float): Time delta to add to the radar timestamps.
      Returns:
        np.ndarray: Interpolated motion capture data. Time has been removed.
    """

    interp_data = []
    last_pos = 0
    for i in range(radar_timestamps.shape[0]):
        found = False
        for j in range(last_pos, mocap_data.shape[0]):
            if mocap_data[j][0] >= radar_timestamps[i] + time_delta:
                interp_data.append(mocap_data[j][1:])
                last_pos = j - 1
                found = True
                break

        if not found:
            # set a position 10000 units away
            interp_data.append([10000, 10000, 10000, 0])

    return np.array(interp_data)


def find_start_end(mocap_data: np.ndarray) -> (int, int):

    # compute velocity in all directions
    vel_x = np.diff(mocap_data[:, 1]) / np.diff(mocap_data[:, 0])
    vel_x = np.convolve(vel_x, np.ones(10), 'same') / 10

    vel_y = np.diff(mocap_data[:, 2]) / np.diff(mocap_data[:, 0])
    vel_y = np.convolve(vel_y, np.ones(10), 'same') / 10

    vel_z = np.diff(mocap_data[:, 3]) / np.diff(mocap_data[:, 0])
    vel_z = np.convolve(vel_z, np.ones(10), 'same') / 10

    vel = vel_x**2 + vel_y**2 + vel_z**2

    vel = np.convolve(vel, np.ones(10), 'same') / 10

    # take average of first 350 frames
    start = 0
    avg = np.mean(vel[:350])
    # find first frame where velocity is greater than 1.5 times the average
    for i in range(len(vel)):
        if abs(vel[i] - avg) > 0.1:
            start = i
            break

    # take average of the last 350 frames
    avg = np.mean(vel[-350:])
    end = 0
    # find last frame where velocity is greater than 1.5 times the average
    for i in range(len(vel) - 1, 0, -1):
        if abs(vel[i] - avg) > 0.1:
            end = i
            break

    return start, end


def normalize_scans(mocap_data: np.ndarray, scan_data: dict) -> np.ndarray:

    start, end = find_start_end(mocap_data)

    # slice the motion capture data
    mocap_data = mocap_data[start:end]

    start_time = mocap_data[start][0]

    # TODO: Figure out how to get the time delta
    time_delta = 0

    # extract the timestamps from the scan data
    radar_timestamps = scan_data["time"]

    # convert to seconds
    radar_timestamps = radar_timestamps - radar_timestamps[0]
    radar_timestamps = radar_timestamps / 1000.0

    # interpolate the motion capture data
    positions = interpolate_mocap_frames(
        mocap_data, radar_timestamps, time_delta)

    # return the interpolated data
    return positions
