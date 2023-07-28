import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import src.lib.read_csv as mocap
from src.backproj.wrapper import BackProj
from src.lib.file_utils import read_data_file
from src.processor.normalize_scans import normalize_scans


# scan data
pkl = read_data_file('data/2023-07-25_15-30-01.pkl')

motion_capture_file_path = 'data/FSmocapP4.csv'
motion_capture_data = mocap.read_csv(
    motion_capture_file_path, "FingerSlicer2")

# motion capture data
# Replace with the actual file path

# Matching motion capture data to scan times
positions = normalize_scans(motion_capture_data, pkl)

# number of timeframes
scan_count = pkl["data"].shape[0]

# Number of scans within a certain time
scan_length = pkl["data"].shape[1]

# flatten data
data = pkl["data"].flatten()
data = np.abs(data)

data = [int(x) for x in data]

positions = positions.flatten()
positions = [float(x) for x in positions]

bin_start = pkl["start"]
bin_end = pkl["end"]
bin_size = 0.009159475944479724


bp = BackProj(data, positions, scan_count, scan_length,
              bin_start, bin_end, bin_size)

dat = np.array(bp.getRegion(-6, -6, 0, 12, 12, 50))

plt.imshow(dat)
plt.show()
