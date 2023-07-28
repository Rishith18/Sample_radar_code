def int_to_bytes(number: int, size: int, signed: bool) -> bytes:
    """Converts an integer to bytes.

        Args:
            number (int): The integer to be converted.
            size (int): The size of the output in bits. Must be one of [8, 16, 24, 32]
            signed: Whether the integer is signed or not.
        Returns:
            A big-endian byte array of the integer.
    """
    # size must be multiple of 8, and max 32
    if size % 8 != 0 or size > 32:
        raise ValueError("Invalid size. Not 8, 16, 24, 32")
    # convert the number to bytes
    return number.to_bytes(size // 8, byteorder='big',  signed=signed)


def bytes_to_int(bytes: bytes, signed: bool) -> int:
    """Converts bytes to an integer.
        Args:
            bytes (bytes): The bytes to be converted.
            signed (bool): Whether the integer is signed or not.
        Returns:
            The integer.
    """
    # convert the bytes to an integer
    return int.from_bytes(bytes, byteorder='big', signed=signed)


def bytes_from_list(parts: list[tuple[int, int, bool]]) -> bytes:
    """Converts a list of integers to bytes.

        Args:
            parts [(int, int, bool)]: A series of tuples describing parts and how to convert them.
        Returns:
            A big-endian byte array of the integers.
    """

    total = bytes()
    for part in parts:
        total += int_to_bytes(part[0], part[1], part[2])
    return total


c = 299792458


def range_to_ps(range: float) -> int:
    """Converts a range in m to picoseconds.

        Args:
            range (float): The range in mm.
        Returns:
            The range in picoseconds.
    """
    seconds = (range * 2) / c
    return int(seconds // 10**-12)


def ps_to_range(ps: int) -> float:
    """Converts a range in picoseconds to m.

        Args:
            ps (int): The range in picoseconds.
        Returns:
            The range in m.
    """
    seconds = ps * 10**-12
    return (seconds * c) / 2
