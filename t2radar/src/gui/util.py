def format_float(value: float, precision=3):
    """Formats a float to a string with the given precision

    Args:
        value (float): The value to format
        precision (int): The precision to use

    Returns:
        The formatted string
    """
    return ("{0:." + str(precision) + "f}").format(value)
