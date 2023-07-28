from collections import deque
from datetime import datetime


class Logger:

    def __init__(self, maxLen=100):
        self.contents = deque(maxlen=maxLen)

    def log(self, message):
        """ Adds a message to the log
            Args:
                message: string

            Returns:
                None
        """

        datestring = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.contents.append(datestring + " " + message)

    def get(self):
        """ Returns the contents of the log
            Args:
                None

            Returns:
                list of strings
        """
        return list(self.contents)

    def clear(self):
        """ Clears the log
            Args:
                None

            Returns:
                None
        """
        self.contents.clear()
