import numpy as np

KERNELS = {
    # vals are standard in image processing
    "identity": np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]]),
    "edge_filter_1": np.array([[-1, -1, -1], [-1, 12, -1], [-1, -1, -1]]),
    "edge_filter_1": np.array([[-1, -1, -1], [-1, 12, -1], [-1, -1, -1]]),
    "edge_filter_2": np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]]),
    "gausian": np.array([[1/16, 1/8, 1/16], [1/8, 1/4, 1/8], [1/16, 1/8, 1/16]])
}


def get_kernel(kernel_name: str):
    """Returns 3x3 matrics coresponding to the provided filter name  
        Args: 
            kernel_name as string
        Returns:
            3x3 filter weights
    """
    if kernel_name in KERNELS:
        return KERNELS[kernel_name]
    else:
        return np.array([])


def apply_filter(radar_data: dict, filter_name: str, filter_threshold=25, normalize=True):
    """Applies a specified filter to the radar data using numpy vectorization
       this uses numpy vectorization to calculate sum of 3x3
       match cell and multiply with corresponding filter value (from kernels)
       sliding 3x3 window is element-wise multiplied by filter matrix and all end results are summed up and stored in the center element of the sliding window
       goes through original data, writes into an empty copy of the 2D array
        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
                where data is a numpy 2D array.
            filter_name - options available: edge_filter_1, edge_filter_2.
            filter_threshold - sets data to 0 for all values below it, applied after filter and normalization.
            normalize - true/false specifies if normalization should be applied to compensate filter adjustments
        Returns:
            filtered radar_data
    """
    data = radar_data["data"]

    # creates a 2D array of zeros that is the same size as the data array
    filtered = np.zeros(data.shape)

    filter_matrix = get_kernel(filter_name)

    # this uses numpy vectorization to calculate sum of 3x3
    # match cell and multiply with corresponding filter value (from kernels)
    # sliding 3x3 window is element-wise multiplied by filter matrix and all end results are summed up and stored in the center element of the sliding window
    # goes through original data, writes into an empty copy of the 2D array
    filtered[1:-1, 1:-1] = (data[:-2, :-2] * filter_matrix[0, 0]) + \
        (data[:-2, 1:-1] * filter_matrix[0, 1]) + \
        (data[:-2, 2:] * filter_matrix[0, 2]) + \
        (data[1:-1, :-2] * filter_matrix[1, 0]) + \
        (data[1:-1, 1:-1] * filter_matrix[1, 1]) + \
        (data[1:-1, 2:] * filter_matrix[1, 2]) + \
        (data[2:, :-2] * filter_matrix[2, 0]) + \
        (data[2:, 1:-1] * filter_matrix[2, 1]) + \
        (data[2:, 2:] * filter_matrix[2, 2])

    # normalization step
    # filtering scrambles the value of cells depending on what filter is used meaning we don't get data that we can easily read
    # this ensures that the target's intensity is somewhat similar before and after filtering
    norm_coef = 1
    if normalize:
        # find maximum pixel intensity of original data
        original_max = np.amax(data)
        # find the maximum pixel intensity of filtered data
        max = np.amax(filtered)
        # find a coeficient that will restore the intensity of the data
        norm_coef = original_max / max

    output = radar_data
    # every element is multiplied by the normalized coeficient
    filtered = filtered * norm_coef

    # apply threashold to set values to 0 for all items below threshold
    filtered[filtered <= filter_threshold] = 0

    output["data"] = filtered
    return output


def apply_log(radar_data: dict):
    radar_data["data"] = 20 * np.log10(np.array(radar_data["data"]))
    return radar_data


def denoise_filter(radar_data: dict, value_threshold=0, count_threshold=1):
    """Eliminate single pixels
        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
            filter_name - options available: edge_filter_1, edge_filter_2
        Returns:
            denoised radar_data
    """
    data = radar_data["data"]

    # remove inactive range values (can change)
    # FIXME: We may not need it for most scans
    # data[:,range(200)] = 0

    # apply threashold to set values to 0 for all cells in 2D array below threshold
    data[data <= value_threshold] = 0

    # create a 3x3 matrix that goes over the entire array looking for
    # make a copy of original 2D array and translate it to 0's and 1's
    mask = np.copy(data)
    # sets all values greater than 0 to 1
    mask[mask > 0] = 1
    mask_counts = np.ones(data.shape)
    # The code below counts the num of pixels that have intensity
    # It determines this num because all values are set to 1 or 0 so if a pixels has any intensity, it will be set to 1
    # which can then be added up, and will tell how many pixels are in the 3x3 matrix
    mask_counts[1:-1, 1:-1] = (mask[:-2, :-2]) + \
        (mask[:-2, 1:-1]) + \
        (mask[:-2, 2:]) + \
        (mask[1:-1, :-2]) + \
        (mask[1:-1, 1:-1]) + \
        (mask[1:-1, 2:]) + \
        (mask[2:, :-2]) + \
        (mask[2:, 1:-1]) + \
        (mask[2:, 2:])

    # tells which pixels need extinguished
    mask_counts[mask_counts <= count_threshold] = 0
    # indicates which pixels can stay lit
    mask_counts[mask_counts > count_threshold] = 1

    filtered = data * mask_counts

    output = radar_data.copy()
    output["data"] = filtered
    return output


def count_pixel_stats(radar_data: dict, first_bucket_threshold, bucket_size):
    """Method counts values in a 2D array bucketed by the provided size, starting with the provided first_bucket_threshold value

        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
            first_bucket_threshold, 
            bucket_size
        Returns:
            a dictionary where key is a number, representing upper bucket limit and a value containing no of items in that bucket  
    """
    data = radar_data["data"]
    data_copy = np.copy(data)

    # remove inactive range values (can change)
    data_copy[:, range(200)] = 0

    # setting value for 1st bucket
    data_copy[data_copy <= first_bucket_threshold] = first_bucket_threshold

    max_value = np.amax(data_copy)

    # creates value ranges(buckets) and sets all values within that bucket to the upper limit of its bucket
    for i in range(1, (round((max_value - first_bucket_threshold) / bucket_size) + 2)):
        lower_limit = first_bucket_threshold + (i - 1) * bucket_size
        upper_limit = first_bucket_threshold + i * bucket_size
        data_copy = np.where((data_copy > lower_limit) & (
            data_copy <= upper_limit), upper_limit, data_copy)

    # counts the number of unique values in the numpy array
    unique, counts = np.unique(data_copy, return_counts=True)
    return dict(zip(unique, counts))


# runs denoise_filter function until a pixel removal threshold is reached
# removing more pixels would result in disrupted target signal
def iterative_denoise(data, value_threshold, count_threshold=4):
    # calc stats
    stats = count_pixel_stats(
        data, first_bucket_threshold=value_threshold, bucket_size=10)

    zero_bucket_before = stats[value_threshold]
    denoised_data = data
    while True:
        denoised_data = denoise_filter(
            radar_data=denoised_data, value_threshold=value_threshold, count_threshold=count_threshold)
        stats_after = count_pixel_stats(
            denoised_data, first_bucket_threshold=value_threshold, bucket_size=5)
        zero_bucket_after = stats_after[value_threshold]
        delta = zero_bucket_after - zero_bucket_before
        zero_bucket_before = zero_bucket_after
        if delta <= 0:
            break

    return denoised_data

def bucketize_radar_data(radar_data: dict, first_bucket_threshold, bucket_size, output_threshold):
    """Method adjusts data by assigning it to appropriate buckets. Buckets are created based on the provided size, 
       starting with the provided first_bucket_threshold value

        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
            first_bucket_threshold, 
            bucket_size
        Returns:
             radar_data - dictionary  
    """
    data = radar_data["data"]
    data_copy = np.copy(data)

    # setting value for 1st bucket
    data_copy[data_copy <= first_bucket_threshold] = first_bucket_threshold

    max_value = np.amax(data_copy)

    # creates value ranges(buckets) and sets all values within that bucket to the upper limit of its bucket
    for i in range(1, (round((max_value - first_bucket_threshold) / bucket_size) + 2)):
        lower_limit = first_bucket_threshold + (i - 1) * bucket_size
        upper_limit = first_bucket_threshold + i * bucket_size
        data_copy = np.where((data_copy > lower_limit) & (
            data_copy <= upper_limit), upper_limit, data_copy)


    # apply threashold to set values to 0 for all cells in 2D array below threshold
    data_copy[data_copy <= output_threshold] = 0

    return {
            "data": data_copy,
            "time": radar_data["time"],
            "start": radar_data["start"],
            "end":  radar_data["end"]
        }


    # apply threashold to set values to 0 for all cells in 2D array below threshold
    data_copy[data_copy <= output_threshold] = 0

    return {
            "data": data_copy,
            "time": radar_data["time"],
            "start": radar_data["start"],
            "end":  radar_data["end"]
        }  
