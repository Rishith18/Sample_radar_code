# this file is used to maintain state across the application
# This isn't exactly pythonic, but it works
from lib.config import get_config


state = {

    # The current config
    "config": get_config()
}


def get_state(key: str):  # python has no "any" type :P
    """Returns the state with the given key

    Args:
        key (str): The key to get

    Returns:
        The value of the state with the given key

    """

    return state[key]


def set_state(key: str, value):
    """Sets the state with the given key and value

    Args:
        key (str): The key to set
        value: The value to set

    """

    state[key] = value
