# t2radar

Repository of scripts for UAS-SAR 2023 by Team 2

# Contents

- `docs` - Specific documentation of library usage
- `src/lib` - Source code for the library
- `src/gui` - Source code for the GUI
- `src/processor` - Soruce code for processing and visualizing data
- `src/backproj` - Vectorized C++ backprojection code
- `src/index.py` - Main script for running in headless mode
- `src/app.py` - Main script for running in GUI mode
- `sh` - Shell scripts for ease-of-use
- `sh/compile` - Shell scripts for compiling the library
- `bin` - Precompiled binaries for the library

# Installation

> Required Python version: 3.10

Run the following commands:

```
git clone git@github.com:bwsiuassar/t2radar.git
cd t2radar
```

The following packages are required (through your pkg manager of choice):

```
numpy
scipy
matplotlib
```

This program uilizes C++ shared libraries for speed. The current supported OS/arch config are below:

- Linux x84_64
- Darwin x84_64
- Darwin arm64

If your system is not included in the above list, you will have to compile the binary yourself, and edit [wrapper.py](/src/backproj/wrapper.py) to load the correct dll/so/dylib for your system.

If your system is included in the list, you can run the appropriate compile shell script [here](/sh/compile/)

# Configuration

This program is configured through a `config.json` file. If one does not exist at boot, it will be created.

When running in GUI mode, edits made to the configuration will be saved automatically.

The following is an example configuration file:

```json
{
  "net": {
    "ip": "192.168.1.151",
    "port": 21210
  },
  "radar": {
    "integrationIndex": 11,
    "scanStart": 26685,
    "scanEnd": 79419,
    "scanInterval": 0,
    "scanCount": 65535,
    "distanceCorrection": -2.0
  },
  "ui": {
    "units": "m"
  }
}
```

# Usage

## Headless Mode

This mode is restricted to running fixed-length scans only. To run a scan, run the following command:

```
python3 src/index.py
```

After the scan is completed, the data file will be placed in the `./data` directory.

## GUI Mode

This mode can run both fixed-length and continuous scans. To launch the application, run the following commend:

```
python3 src/app.py
```

# Save file format

Files are saved in the pickle (`pkl`) format. This file consists of one "header" object followed by many "data" objects.

The header object contains the following fields:

```json
{
  "point_count": 0,
  "frame_count": 0,
  "start_range": 0.0,
  "end_range": 0.0
}
```

- `point_count` - The number of data points in each frame
- `frame_count` - The number of frames the follow in the file
- `start_range` - The starting range of the scan (meters)
- `end_range` - The ending range of the scan (meters)

The data object contains the following fields:

```json
{
  "timestamp": 0.0,
  "data": []
}
```

- `timestamp` - The relative timestamp of the frame (ms)
- `data` - The data points of the frame in a 1D NumPy array
