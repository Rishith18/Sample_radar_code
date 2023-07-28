from collections import deque
from random import randint


def get_last_valid_index(data: list[int]) -> int:
    # move backwards through the list
    for i in range(len(data) - 1, -1, -1):
        if data[i] != 0:
            return i


def trim_data(data: deque[dict]):
    """Trims trailing 0-pads from scan data.
      Args:
          data (deque): A deque of data sets
      Returns:
          A deque of data sets with trailing 0-pads removed
    """

    # determine the last valid index

    # if there are more than 100 data points, select 100 random points
    # this is for optimization purposes
    zero_indexes = []

    if len(data) > 100:
        for _ in range(100):

            # get a random index
            index = randint(0, len(data) - 1)

            # get the last valid index
            last_valid_index = get_last_valid_index(data[index]["data"])
            zero_indexes.append(last_valid_index)

    else:

        for element in data:
            last_valid_index = get_last_valid_index(element["data"])
            zero_indexes.append(last_valid_index)

    # get the max zero index
    max_zero_index = max(zero_indexes)

    # remove the 0-pads
    for element in data:
        element["data"] = element["data"][0:max_zero_index]

    return data
