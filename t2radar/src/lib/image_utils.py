import numpy as np
import file_utils as futile

def get_radar_start_time(radar_data: dict):
    """Analyses radar data to capture the time of the first movement
        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
                where data is a numpy 2D array.
        Returns:
            the time at which motion is detected for the first time
    """
    time = np.array(radar_data["time"])
    corr = get_correlations(radar_data)


    #apply moving window filter
    corr = running_mean(np.array(corr), 10).tolist()

    corr = corr[5:len(corr)-5]

    #finds the first instance of a correlation below .85 (works for 30-01.pkl, not sure about others)
    idx = next(x[0] for x in enumerate(corr) if x[1] < 0.85)

    # radar_data = radar_data[]
    radar_data["data"] = radar_data["data"][idx:-1]
    radar_data["time"] = radar_data["time"][idx:-1]

    return radar_data

def get_correlations(radar_data: dict):
    """Calculates correlation coeficients between every two consecutive rows 
        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
                where data is a numpy 2D array.
        Returns:
            an 1D array containing max correlation value per each row 
    """
    data = radar_data["data"] 

    max_corr_vals = []
    for i in range(1, len(data)-1):
        #calculates similarity shifting to the left
        calc_similarity_L = statistical_correlation(data[i-1], data[i])
        #calculates similarity shifting to the right
        calc_similarity_R = statistical_correlation(data[i], data[i-1])
        #picking the max value from the above correlation coefs. 
        #max_corr_val_array.append(max(max(calc_similarity_R),max(calc_similarity_L)))

        max_corr = max(max(calc_similarity_R),max(calc_similarity_L))
        max_corr_vals.append(max_corr) 
    return max_corr_vals

def statistical_correlation(x, y, n=8):
    """Calculates statistical correlation between given two arrays, shifting a second array left by n elements
    https://stackoverflow.com/questions/643699/how-can-i-use-numpy-correlate-to-do-autocorrelation
    Args: 
            x,y - 1D arrays to compare, have to be of same length
        Returns:
            correlation results in 1D array, where values are in [0,1], 1 meaning arrays are identical.
    """
    return np.array([np.corrcoef(x, y)[0,1]]+[np.corrcoef(x[:-i], y[i:])[0,1]
        for i in range(1, n)])

def running_mean(x, N):
    """Calculates statistical correlation between given two arrays, shifting a second array left by n elements
    Args: 
            x - 1D arrays to apply moving avg
        Returns:
            1D array with averaged data.
    """
    kernel_size = N
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(x, kernel, mode='same')

get_radar_start_time(futile.read_data_file('/Users/rishithprathi/Downloads/t2radar/data/2023-07-25_15-30-01.pkl'))