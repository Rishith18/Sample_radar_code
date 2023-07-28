import numpy as np
import array
from ctypes import *


# get OS & architecture
import platform
import struct

os = platform.system()
arch = platform.machine()

print("OS: " + os)
print("Architecture: " + str(arch))

lib = None
if os == "Linux" and arch == "x86_64":
    lib = cdll.LoadLibrary('./bin/backproj_linux64.so')
    print("Loaded Linux 64-bit library")
if os == "Darwin" and arch == "arm64":
    lib = cdll.LoadLibrary("./bin/backproj_darwinarm64.dylib")
    print("Loaded Apple ARM64 library")
if os == "Darwin" and arch == "x86_64":
    lib = cdll.LoadLibrary("./bin/backproj_darwin64.dylib")
    print("Loaded Apple 64-bit library")


# Lib.getRegion takes the following arguments:
# (int *scans, float *positions, int scanCount, int scanLength, float binStart, float binEnd, float binSize, float x, float y, float width, float length, float resolution)
lib.bp_getRegion.argtypes = [
    POINTER(c_int32), POINTER(c_float), c_int, c_int, c_float, c_float, c_float,  c_float, c_float, c_float, c_float, c_float, c_float]


# returns a list of longs
lib.bp_getRegion.restype = POINTER(c_int64)

# Lib.BackProj_getDim takes the same arguments as Lib.BackProj_getRegion
lib.bp_getDim.argtypes = [c_float, c_float, c_float, c_float, c_float]

# but returns an int
lib.bp_getDim.restype = POINTER(c_int)


class BackProj(object):
    def __init__(self, scans: list[int], positions: list[float], scanCount: int, scanLength: int, binStart: float, binEnd: float, binSize: float):
        # convert to corrct types using array
        scans = array.array('i', scans)
        scans = (c_int32 * len(scans)).from_buffer(scans)

        positions = array.array('f', positions)
        positions = (c_float * len(positions)).from_buffer(positions)

        self.scans = scans
        self.positions = positions
        self.scanCount = scanCount
        self.scanLength = scanLength
        self.binStart = binStart
        self.binEnd = binEnd
        self.binSize = binSize

    def getRegion(self, x: float, y: float, z: float, width: float, height: float, resolution: float) -> list[float]:

        dim = lib.bp_getDim(x, y, width, height, resolution)

        pix_width = dim[0]
        pix_height = dim[1]

        # we get a pointer to the first element of the array
        # and then we cast it to a pointer to a float
        data = lib.bp_getRegion(self.scans, self.positions, self.scanCount, self.scanLength,
                                self.binStart, self.binEnd, self.binSize, x, y, z, width, height, resolution)

        # we got a pointer back, so we need to dereference it
        # and then we need to convert it to a list
        data = np.ctypeslib.as_array(data, shape=(
            pix_height, pix_width))

        print(pix_width, pix_height, "img dim")

        return data
