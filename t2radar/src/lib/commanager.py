from collections import deque
from lib.mrmapi import get_outgoing, resolve_name, mrmapi, get_incoming
from lib.radario import send_payload, recv_payload
import numpy as np

# Handles all communication with the Radio


class commanager:
    mode = "sync"  # sync or async
    databuffer = deque()  # buffer for samples sent from the radar
    nextmsgid = 0  # the next message ID to use
    packet_buckets = {}  # buckets for packets that need to be processed
    bucket_contents = []  # contents of the buckets
    shutdown_mode = False  # whether or we are in the process of shutting down

    def __init__(self) -> None:
        self.mode = "sync"

    def __gen_msg_id__(self) -> int:
        """Generates a message ID.

        Returns:
            The message ID.
        """
        self.nextmsgid += 1
        return self.nextmsgid

    def __reset__(self):
        """ Resets bac to defaults"""

        self.mode = "sync"
        self.databuffer = deque()
        self.nextmsgid = 0
        self.packet_buckets = {}
        self.bucket_contents = []
        self.shutdown_mode = False

    # Send a sync message to the radar

    def send_sync(self, msgtype: int or str, noreply: bool,  **kwargs) -> dict:
        """ Sends a message to the radar and waits for a response.

        Args:
            msgtype (int or str): The message type.
            noreply (bool): Whether or not to wait for a response.
            **kwargs: The message arguments.

        Returns:
            The response payload.
        """

        # grab the relevant outgoing processor
        process_func = get_outgoing(msgtype)

        # if msgtype is a string, resolve it to an int
        if isinstance(msgtype, str):
            msgtype = resolve_name(msgtype)

        # generate a message ID
        msgid = self.__gen_msg_id__()

        # process the message
        payload = process_func["func"](**kwargs)

        # send it off
        send_payload(msgtype, msgid, payload)

        # check if we need to wait for a response
        targetID = process_func["responseID"]

        if targetID == None or noreply:
            return {}

        # UDP doesn't guarantee that packets are recieved in order,
        # so we need to keep processing incoming packets until we get
        # the one we want

        # However, this is probably only going to happen with
        # MRM_SCAN_INFO and MRM_READY_INFO
        # Since now we probably don't care about the data in the
        # other packets, we can just discard them

        while True:
            msgtype, _msgid, payload = recv_payload()

            # if we get a good response or error packet
            if msgtype == targetID or msgtype == 0xF10C:

                # we shouldn't be sending out more than one sync message at a time
                # but just in case, we'll check the message ID

                if _msgid != msgid:
                    print("WARNING: Message ID mismatch!")
                    print("Expected: " + str(msgid))
                    print("Sync mode has been broken!")

                    # this is a fatal error
                    # we can't recover from this
                    exit(1)

                break

        # grab the relevant incoming processor
        process_func = get_incoming(msgtype)

        # process the message
        return process_func(payload)

    # tick func for async mode
    def get_data(self, num_scans=100000000) -> bool:  # 10^8 is used for Inf
        """Gets data from the radar. Data is stored in the databuffer.

        Args:
            num_scans (int): The number of scans to get.

        Returns:
            Whether or not it needs to be called again.
        """

        # check if we are in async mode
        if self.mode != "async":
            print("WARNING: get_data() called while not in async mode!")
            return False

        # at this point, all sync calls should have been finished,
        # and the only kind of packets we should be getting are
        # MRM_SCAN_INFO and MRM_SET_SLEEPMODE_CONFIRM
        # (with the latter only if we are trying to sleep the radar
        # and end the session)

        # process the incoming data

        # the parts of a larger data set may be jumbled,
        # so we might need to reassmble them

        # grab the next packet
        # except on socket timeout
        try:
            msgtype, msgid, payload = recv_payload()
        except TimeoutError:
            # If we got here, we're no longer getting any data from the radar
            return False

        # if we get a MRM_SET_SLEEPMODE_CONFIRM or MRM_CONTROL_CONFIRM
        # go into shutdown mode
        if msgtype == 0xF10C or msgtype == 0xF10B:
            self.shutdown_mode = True

        # check if it's not MRM_SCAN_INFO
        if msgtype != 0xF201:
            # ignore it
            return True

        # parse it
        data = mrmapi.MRM_SCAN_INFO(payload)

        # check if we've seen this bucket before
        timestamp = data["timestamp"]
        if timestamp not in self.bucket_contents:
            # create a new bucket
            self.packet_buckets[timestamp] = {
                "totalParts": data["messageCount"],
                "partsFound": 1,
                "data": [{
                    "index": data["messageIndex"],
                    "data": data["scanData"]
                }]
            }
            self.bucket_contents.append(timestamp)

        else:

            self.packet_buckets[timestamp]["partsFound"] += 1
            self.packet_buckets[timestamp]["data"].append({
                "index": data["messageIndex"],
                "data": data["scanData"]
            })

        # check if we've found all the parts
        if self.packet_buckets[timestamp]["partsFound"] == self.packet_buckets[timestamp]["totalParts"]:
            # we have all the parts, so we can reassemble the data

            # sort the data
            self.packet_buckets[timestamp]["data"].sort(
                key=lambda x: x["index"])

            # reassemble the data
            data = []

            for part in self.packet_buckets[timestamp]["data"]:
                data += part["data"]

            # add it to the buffer
            self.databuffer.append({
                "timestamp": timestamp,
                "data": np.array(data)
            })

            # remove the bucket
            del self.packet_buckets[timestamp]
            self.bucket_contents.remove(timestamp)

        # look for old buckets
        for _timestamp in self.bucket_contents:

            # older than 3 seconds
            if _timestamp < timestamp - 3000:
                # remove the bucket
                del self.packet_buckets[_timestamp]
                self.bucket_contents.remove(_timestamp)
                print(
                    f"WARNING: Discarded scan {_timestamp} due to missing packets!")

        # are we done?
        if num_scans <= len(self.databuffer):
            return False
        else:
            return True

    # the following are metafunctions
    def init_radar(self, **kwargs):
        """Initializes the radar.
          Args:
              **kwargs: Keyword arguments for config
          Returns
              None
        """

        # set configuration
        print("Setting configuration...")
        self.send_sync("MRM_SET_CONFIG_REQUEST", False, **kwargs)

        # get back configuration
        print("Getting new configuration...")
        config = self.send_sync("MRM_GET_CONFIG_REQUEST", False)
        return config

    def exec_scan(self, scan_count: int, scan_interval: int) -> deque:
        """Executes a scan.
          Args:
              scan_count (int): Number of scans to execute
              scanInterval (int): Time between scans
          Returns:
              A deque of data sets
        """

        # data validation on scan_count

        # can't be 0
        if scan_count == 0:
            print("ERROR: scan_count can't be 0!")
            return None

        # can't be greater than 65535
        if scan_count > 65535:
            print("ERROR: scan_count can't be greater than 65534!")
            return None

        if scan_count == 65535:
            print("WARNING: Staring in Infinite Mode")

        # start the scan
        print("Starting scan...")
        self.send_sync("MRM_CONTROL_REQUEST", False,
                       scanCount=scan_count, scanIntervalTime=scan_interval)

        # switch to async mode
        self.mode = "async"

        # get the data
        print("Getting data...")
        while self.get_data(scan_count):
            pass

        self.__resolve__buffers__()

        # switch back to sync mode
        self.mode = "sync"

        print("Done!")

        # return the data
        return self.databuffer

    def sleep_radar(self):
        """Puts the radar to sleep."""

        # set the sleep mode
        print("Setting sleep mode...")
        self.send_sync("MRM_SET_SLEEPMODE_REQUEST", False, mode=1)

        # double check that the radar is asleep
        resp = self.send_sync("MRM_GET_SLEEPMODE_REQUEST", False)

        if resp["sleepMode"] != 1:
            print("ERROR: Radar failed to sleep!")

    def wake_radar(self):
        """Wakes up the radar."""

        # set the sleep mode
        print("Setting sleep mode...")
        self.send_sync("MRM_SET_SLEEPMODE_REQUEST", False, mode=0)

        # await the MRM_READY_INFO packet
        while True:
            msgtype, payload = self.recv_sync()

            # FIXME: This can potentially cause issues with lost packets
            if msgtype == 0xF202:
                break

        # double check that the radar is awake
        resp = self.send_sync("MRM_GET_SLEEPMODE_REQUEST", False)

        if resp["sleepMode"] != 0:
            print("ERROR: Radar failed to wake!")
