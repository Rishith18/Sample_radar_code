import numpy as np
import matplotlib.pyplot as plt

#def generate_heatmap(filePath: str, unit="m", threshold = None, tv_weight=0.1):
def generate_heatmap(radar_data: dict, unit="m"):
    data = radar_data["data"]
    times = radar_data["time"]
    start = radar_data["start"]
    end = radar_data["end"]
    (rows,cols) = data.shape


    # get max in data
    max = np.amax(data)
    # get min in data you machine
    min = np.amin(data)

    # plot the data in a heatmap using pcolor
    plt.pcolor(data, vmin=min, vmax=max)

    # scale the color bar according to min and max
    plt.clim(0, max)

    plt.colorbar()

    plt.title("Range Time Intensity")
    plt.xlabel(f"Range ({unit})")
    plt.ylabel("Time Elapsed (s)")

    # use set_aspect to strech y axis
    plt.gca().set_aspect(cols/rows)

    num_ticks = 10  # Number of desired ticks

    # Modify tick locations and labels on the x-axis
    tick_locations = np.linspace(start, cols - 1, num_ticks)

    if unit == "m":
        tick_labels = np.round(np.linspace(start, end, num_ticks), decimals=2)
    else:
        # convert to ft
        tick_labels = np.round(np.linspace(
            start * 3.28084, end * 3.28084, num_ticks), decimals=2)

    plt.xticks(tick_locations, tick_labels)

    # Modify tick locations and labels on the y-axis
    tick_locations = np.linspace(0, rows - 1, num_ticks)
    tick_labels = np.round(np.linspace(
        0, (times[-1] - times[0]) / 1000.0, num_ticks), decimals=2)
    plt.yticks(tick_locations, tick_labels)



    plt.show()

