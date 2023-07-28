# MRM API functions
from lib.util import bytes_to_int, bytes_from_list

# MRM API functions
# For more information, see the MRM API documentation
# https://tdsr-uwb.com/wp-content/uploads/2021/03/320-0298G-MRM-API-Specification.pdf


class mrmapi:

    # ID 0x1001
    def MRM_SET_CONFIG_REQUEST(nodeID=5, scanStart=0, scanEnd=5, scanResolution=32, baseIntegrationIndex=6,
                               antennaMode=2, transmitGain=0, codeChannel=7, persistFlag=0) -> bytes:
        """compiles a MRM_SET_CONFIG_REQUEST packet
            Args:
                nodeID (int): Node ID
                scanStart (int): Start of scan in picoseconds
                scanEnd (int): End of scan in picoseconds
                scanResolution (int): Resolution of scan in picoseconds
                baseIntegrationIndex (int): Base integration index
                antennaMode (int): Antenna mode
                transmitGain (int): Transmit gain
                codeChannel (int): Code channel
                persistFlag (int): Persist flag
            Returns:
                A bytes object containing the packet
        """

        params = [
            [nodeID, 32, False],
            [scanStart, 32, True],
            [scanEnd, 32, True],
            [scanResolution, 16, False],
            [baseIntegrationIndex, 16, False],

            # between these comments are NYI parameters
            [0, 16, False],
            [0, 16, False],
            [0, 16, False],
            [0, 16, False],
            [0, 8, False],
            [0, 8, False],
            [0, 8, False],
            [0, 8, False],
            # end NYI parameters

            [antennaMode, 8, False],
            [transmitGain, 8, False],
            [codeChannel, 8, False],
            [persistFlag, 8, False]
        ]

        return bytes_from_list(params)

    # ID 0x1101

    def MRM_SET_CONFIG_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_SET_CONFIG_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        status = bytes_to_int(payload[0:4], False)
        return {"status": status}

    # ID 0x1002

    def MRM_GET_CONFIG_REQUEST() -> bytes:
        """compiles a MRM_GET_CONFIG_REQUEST packet
            Returns:
                A bytes object containing the packet
        """

        return bytes()

    # ID 0x1102

    def MRM_GET_CONFIG_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_GET_CONFIG_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """
        nodeID = bytes_to_int(payload[0:4], False)
        scanStart = bytes_to_int(payload[4:8], True)
        scanEnd = bytes_to_int(payload[8:12], True)
        scanResolution = bytes_to_int(payload[12:14], False)
        baseIntegrationIndex = bytes_to_int(payload[14:16], False)
        antennaMode = bytes_to_int(payload[28:29], False)
        transmitGain = bytes_to_int(payload[29:30], False)
        codeChannel = bytes_to_int(payload[30:31], False)
        persistFlag = bytes_to_int(payload[31:32], False)
        timestamp = bytes_to_int(payload[32:36], False)
        status = bytes_to_int(payload[36:40], False)

        return {
            "nodeID": nodeID,
            "scanStart": scanStart,
            "scanEnd": scanEnd,
            "scanResolution": scanResolution,
            "baseIntegrationIndex": baseIntegrationIndex,
            "antennaMode": antennaMode,
            "transmitGain": transmitGain,
            "codeChannel": codeChannel,
            "persistFlag": persistFlag,
            "timestamp": timestamp,
            "status": status
        }

    # ID 0x1003

    def MRM_CONTROL_REQUEST(scanCount=1, scanIntervalTime=0) -> bytes:
        """compiles a MRM_CONTROL_REQUEST packet
            Args:
                scanCount (int): Number of scans to perform
                scanIntervalTime (int): Time between scans in microseconds
            Returns:
                A bytes object containing the packet
        """

        params = [
            [scanCount, 16, False],
            [0, 16, False],
            [scanIntervalTime, 32, False]
        ]

        return bytes_from_list(params)

    # ID 0x1103

    def MRM_CONTROL_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_CONTROL_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:    
                A dictionary containing the decoded packet
        """

        status = bytes_to_int(payload[0:4], False)
        return {"status": status}

    # ID 0x1004

    def MRM_SERVER_CONNECT_REQUEST(ipaddr=(192, 168, 1, 151), port=21210) -> bytes:
        """compiles a MRM_SERVER_CONNECT_REQUEST packet
            Args:
                ipaddr (int, int, int, int): IP address of the server
                port (int): Port of the server    
            Returns:
                A bytes object containing the packet
        """

        params = [
            [ipaddr[0], 8, False],
            [ipaddr[1], 8, False],
            [ipaddr[2], 8, False],
            [ipaddr[3], 8, False],
            [port, 16, False],
            [0, 16, False]
        ]

        return bytes_from_list(params)

    # ID 0x1104

    def MRM_SERVER_CONNECT_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_SERVER_CONNECT_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        connectionStatus = bytes_to_int(payload[0:4], False)
        return {connectionStatus}

    # ID 0x1005

    def MRM_SERVER_DISCONNECT_REQUEST() -> bytes:
        """compiles a MRM_SERVER_DISCONNECT_REQUEST packet
            Returns:
                A bytes object containing the packet
        """

        return bytes()

    # ID 0x1105

    def MRM_SERVER_DISCONNECT_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_SERVER_DISCONNECT_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        status = bytes_to_int(payload[0:4], False)
        return {"status": status}

    # ID 0x1006

    def MRM_SET_FILTER_CONFIG_REQUEST(filterMask=1, motionFilterIndex=0) -> bytes:
        """compiles a MRM_SET_FILTER_CONFIG_REQUEST packet
            Args:
                filterMask (int): Filter mask
                motionFilterIndex (int): Motion filter index  
            Returns:
                A bytes object containing the packet
        """

        params = [
            [filterMask, 32, False],
            [motionFilterIndex, 16, False],
            [0, 16, False]
        ]

        return bytes_from_list(params)

    # ID 0x1106

    def MRM_SET_FILTER_CONFIG_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_SET_FILTER_CONFIG_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        status = bytes_to_int(payload[0:4], False)
        return {"status": status}

    # ID 0x1007

    def MRM_GET_FILTER_CONFIG_REQUEST() -> bytes:
        """compiles a MRM_GET_FILTER_CONFIG_REQUEST packet
            Returns:
                A bytes object containing the packet
        """

        return bytes()

    # ID 0x1107

    def MRM_GET_FILTER_CONFIG_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_GET_FILTER_CONFIG_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        filterMask = bytes_to_int(payload[0:2], False)
        motionFilterIndex = bytes_to_int(payload[2:3], False)
        status = bytes_to_int(payload[4:8], False)

        return {
            "filterMask": filterMask,
            "motionFilterIndex": motionFilterIndex,
            "status": status
        }

    # ID 0xF001

    def MRM_GET_STATUSINFO_REQUEST() -> bytes:
        """compiles a MRM_GET_STATUSINFO_REQUEST packet 
            Returns:
                A bytes object containing the packet
        """

        return bytes()

    # ID 0xF101

    def MRM_GET_STATUSINFO_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_GET_STATUSINFO_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        mrmVersionMajor = bytes_to_int(payload[0:1], False)
        mrmVersionMinor = bytes_to_int(payload[1:2], False)
        mrmVersionBuild = bytes_to_int(payload[2:4], False)
        uwbKernelMajor = bytes_to_int(payload[4:5], False)
        uwbKernelMinor = bytes_to_int(payload[5:6], False)
        uwbKernelBuild = bytes_to_int(payload[6:8], False)
        fpgaFirmwareVersion = bytes_to_int(payload[8:9], False)
        fpgaFirmwareYear = bytes_to_int(payload[9:10], False)
        fpgaFirmwareMonth = bytes_to_int(payload[10:11], False)
        fpgaFirmwareDay = bytes_to_int(payload[11:12], False)
        serialNumber = bytes_to_int(payload[12:16], False)
        boardRevision = bytes_to_int(payload[16:17], False)
        bitTestResult = bytes_to_int(payload[17:18], False)
        boardType = bytes_to_int(payload[18:19], False)
        transmitterConfig = bytes_to_int(payload[19:20], False)
        temperature = bytes_to_int(payload[20:24], True)
        # next 32 bytes are 1 char each
        packageVersion = ""
        for pos in range(24, 56):
            packageVersion += chr(payload[pos])

        status = bytes_to_int(payload[56:60], False)

        return {
            "mrmVersionMajor": mrmVersionMajor,
            "mrmVersionMinor": mrmVersionMinor,
            "mrmVersionBuild": mrmVersionBuild,
            "uwbKernelMajor": uwbKernelMajor,
            "uwbKernelMinor": uwbKernelMinor,
            "uwbKernelBuild": uwbKernelBuild,
            "fpgaFirmwareVersion": fpgaFirmwareVersion,
            "fpgaFirmwareYear": fpgaFirmwareYear,
            "fpgaFirmwareMonth": fpgaFirmwareMonth,
            "fpgaFirmwareDay": fpgaFirmwareDay,
            "serialNumber": serialNumber,
            "boardRevision": boardRevision,
            "bitTestResult": bitTestResult,
            "boardType": boardType,
            "transmitterConfig": transmitterConfig,
            "temperature": temperature,
            "packageVersion": packageVersion,
            "status": status
        }

    # ID 0xF002

    def MRM_REBOOT_REQUEST() -> bytes:
        """compiles a MRM_REBOOT_REQUEST packet
            Returns:
                A bytes object containing the packet
        """

        return bytes()

    # ID 0xF102

    def MRM_REBOOT_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_REBOOT_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        status = bytes_to_int(payload[0:4], False)
        return {"status": status}

    # ID 0xF003

    def MRM_SET_OPMODE_REQUEST(opMode=1) -> bytes:
        """compiles a MRM_SET_OPMODE_REQUEST packet
            Args:
                opMode (int): The opMode to set
            Returns:
                A bytes object containing the packet
        """

        params = [
            [opMode, 32, False]
        ]

        return bytes_from_list(params)

    # ID 0xF103

    def MRM_SET_OPMODE_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_SET_OPMODE_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        opmode = bytes_to_int(payload[0:4], False)
        status = bytes_to_int(payload[4:8], False)

        return {
            "opmode": opmode,
            "status": status
        }

    # ID 0xF201

    def MRM_SCAN_INFO(payload: bytes) -> dict:
        """decodes a MRM_SCAN_INFO packet
            Args:
                payload (bytes): The payload of the packet
            Returns:    
                A dictionary containing the decoded packet
        """

        sourceID = bytes_to_int(payload[0:4], False)
        timestamp = bytes_to_int(payload[4:8], False)
        # next 16 bytes are reserved
        scanStart = bytes_to_int(payload[24:28], True)
        scanStop = bytes_to_int(payload[28:32], True)
        scanStep = bytes_to_int(payload[32:34], True)
        scanType = bytes_to_int(payload[34:35], False)
        # 1 byte reserved
        antennaID = bytes_to_int(payload[36:37], False)
        operationalMode = bytes_to_int(payload[37:38], False)

        # here is where we go off-track for a bit
        # next section describes how much data we got
        # and the data itself

        numMessageSamples = bytes_to_int(payload[38:40], False)
        numTotalSamples = bytes_to_int(payload[40:44], False)

        # these next two basically tell us how many total messages
        # and which message we are on
        messageIndex = bytes_to_int(payload[44:46], False)
        messageCount = bytes_to_int(payload[46:48], False)

        # now we are onto scan data
        scanData = []
        for pos in range(48, len(payload), 4):
            scanData.append(bytes_to_int(payload[pos:pos+4], True))

        return {
            "sourceID": sourceID,
            "timestamp": timestamp,
            "scanStart": scanStart,
            "scanStop": scanStop,
            "scanStep": scanStep,
            "scanType": scanType,
            "antennaID": antennaID,
            "operationalMode": operationalMode,
            "numMessageSamples": numMessageSamples,
            "numTotalSamples": numTotalSamples,
            "messageIndex": messageIndex,
            "messageCount": messageCount,
            "scanData": scanData
        }

    # ID 0x1201

    def MRM_DETECTION_LIST_INFO(payload: bytes) -> dict:
        """decodes a MRM_DETECTION_LIST_INFO packet 
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        numDetections = bytes_to_int(payload[0:2], False)

        # the rest of the payload is made up of
        # 4 byte detection records. The end is
        # padded with 0s if the number of detections
        # is below 350

        detections = []
        for pos in range(2, len(numDetections * 4), 4):
            index = bytes_to_int(payload[pos:pos+2], False)
            magnitude = bytes_to_int(payload[pos+2:pos+4], True)
            detections.append({"index": index, "magnitude": magnitude})

        return {
            "numDetections": numDetections,
            "detections": detections
        }

    # ID 0xF005

    def MRM_SET_SLEEPMODE_REQUEST(mode=1) -> bytes:
        """compiles a MRM_SET_SLEEPMODE_REQUEST packet
            Args:
                mode (int): The sleep mode to set
            Returns:
                A bytes object containing the packet
        """

        # additional warning to make sure we don't accidentally
        # lose connection to the device

        if (mode == 3 or mode == 4):
            print("WARNING: Setting sleep mode to 3 or 4 will cause the device to stop responding to Ethernet commands!")
            print("Mode will be set to 1 (IDLE) instead!")
            mode = 1

        params = [
            [mode, 32, False]
        ]

        return bytes_from_list(params)

    # ID 0xF105

    def MRM_SET_SLEEPMODE_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_SET_SLEEPMODE_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        status = bytes_to_int(payload[0:4], False)
        return {"status": status}

    # ID 0xF006

    def MRM_GET_SLEEPMODE_REQUEST() -> bytes:
        """compiles a MRM_GET_SLEEPMODE_REQUEST packet
            Returns:
                A bytes object containing the packet
        """

        return bytes()

    # ID 0xF106

    def MRM_GET_SLEEPMODE_CONFIRM(payload: bytes) -> dict:
        """decodes a MRM_GET_SLEEPMODE_CONFIRM packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        sleepMode = bytes_to_int(payload[0:4], False)
        status = bytes_to_int(payload[4:8], False)

        return {
            "sleepMode": sleepMode,
            "status": status
        }

    # ID 0xF202

    def MRM_READY_INFO(payload: bytes) -> dict:
        """decodes a MRM_READY_INFO packet
            Args:
                payload (bytes): The payload of the packet
            Returns:
                A dictionary containing the decoded packet
        """

        return {}

    # ID 0xF10C
    # This is the "mystery packet"
    # It's sent instead of the actual response when an error is detected
    # Generally we never want this to be sent

    def MRM_GENERROR(payload: bytes) -> dict:
        """decodes a MRM_GENERROR packet
            Args:
                payload (bytes): The payload of the packet
            Returns:    
                A dictionary containing the decoded packet
        """

        targetMessageType = bytes_to_int(payload[0:2], False)
        targetMessageID = bytes_to_int(payload[2:4], False)
        errorCode = bytes_to_int(payload[4:8], False)

        # detect if it's an internal error (0x80000000)
        if (errorCode & 0x80000000 == 0x80000000):
            # here is where it gets especially nasty
            # the given error code is actully OR'd with 0x80000000
            # so we have to sus that out
            errorCode = errorCode & 0x7FFFFFFF
            print("WARNING! Internal Error Detected!")
            print(
                "This is a bug in the MRM API and should be reported to the manufacturer!")
            print(f"Error Code: {errorCode}")

            # stop the program from continuing to avoid any further issues
            exit()

        print("Message Error!\nOffending Message Info:")
        print(
            f"Type: {hex(targetMessageType)}\n MessageID: {targetMessageID}\n Error Code: {errorCode}")

        return {
            "targetMessageType": targetMessageType,
            "targetMessageID": targetMessageID,
            "errorCode": errorCode
        }


# function bank

outgoing_func_bank = {}
incoming_func_bank = {}


def __add_to_outgoing(msgtype: int, func: callable, responseid: int = None):
    """"registers" a function to be called when a packet is sent
        Args:
            msgtype: The message type to register the function to
            func: The function to call
            responseid: The message ID to send in the response
    """

    outgoing_func_bank[msgtype] = {
        "func": func,
        "responseID": responseid
    }


def __add_to_incoming(msgtype: int, func: callable):
    """"registers" a function to be called when a packet is received
        Args:
            msgtype: The message type to register the function to
            func: The function to call
    """

    incoming_func_bank[msgtype] = func


# fill up the bank
__add_to_outgoing(0x1001, mrmapi.MRM_SET_CONFIG_REQUEST, 0x1101)
__add_to_outgoing(0x1002, mrmapi.MRM_GET_CONFIG_REQUEST, 0x1102)
__add_to_outgoing(0x1003, mrmapi.MRM_CONTROL_REQUEST, 0x1103)
__add_to_outgoing(0x1004, mrmapi.MRM_SERVER_CONNECT_REQUEST, 0x1104)
__add_to_outgoing(0x1005, mrmapi.MRM_SERVER_DISCONNECT_REQUEST, 0x1105)
__add_to_outgoing(0x1006, mrmapi.MRM_SET_FILTER_CONFIG_REQUEST, 0x1106)
__add_to_outgoing(0x1007, mrmapi.MRM_GET_FILTER_CONFIG_REQUEST, 0x1107)
__add_to_outgoing(0xF001, mrmapi.MRM_GET_STATUSINFO_REQUEST, 0xF101)
__add_to_outgoing(0xF002, mrmapi.MRM_REBOOT_REQUEST, 0xF102)
__add_to_outgoing(0xF003, mrmapi.MRM_SET_OPMODE_REQUEST, 0xF103)
__add_to_outgoing(0xF005, mrmapi.MRM_SET_SLEEPMODE_REQUEST, 0xF105)
__add_to_outgoing(0xF006, mrmapi.MRM_GET_SLEEPMODE_REQUEST, 0xF106)

__add_to_incoming(0x1101, mrmapi.MRM_SET_CONFIG_CONFIRM)
__add_to_incoming(0x1102, mrmapi.MRM_GET_CONFIG_CONFIRM)
__add_to_incoming(0x1103, mrmapi.MRM_CONTROL_CONFIRM)
__add_to_incoming(0x1104, mrmapi.MRM_SERVER_CONNECT_CONFIRM)
__add_to_incoming(0x1105, mrmapi.MRM_SERVER_DISCONNECT_CONFIRM)
__add_to_incoming(0x1106, mrmapi.MRM_SET_FILTER_CONFIG_CONFIRM)
__add_to_incoming(0x1107, mrmapi.MRM_GET_FILTER_CONFIG_CONFIRM)
__add_to_incoming(0xF101, mrmapi.MRM_GET_STATUSINFO_CONFIRM)
__add_to_incoming(0xF102, mrmapi.MRM_REBOOT_CONFIRM)
__add_to_incoming(0xF103, mrmapi.MRM_SET_OPMODE_CONFIRM)
__add_to_incoming(0xF201, mrmapi.MRM_SCAN_INFO)
__add_to_incoming(0xF105, mrmapi.MRM_SET_SLEEPMODE_CONFIRM)
__add_to_incoming(0xF106, mrmapi.MRM_GET_SLEEPMODE_CONFIRM)
__add_to_incoming(0xF202, mrmapi.MRM_READY_INFO)
__add_to_incoming(0xF10C, mrmapi.MRM_GENERROR)


# dict of ID: name
message_types = {
    0x1001: "MRM_SET_CONFIG_REQUEST",
    0x1002: "MRM_GET_CONFIG_REQUEST",
    0x1003: "MRM_CONTROL_REQUEST",
    0x1004: "MRM_SERVER_CONNECT_REQUEST",
    0x1005: "MRM_SERVER_DISCONNECT_REQUEST",
    0x1006: "MRM_SET_FILTER_CONFIG_REQUEST",
    0x1007: "MRM_GET_FILTER_CONFIG_REQUEST",
    0x1101: "MRM_SET_CONFIG_CONFIRM",
    0x1102: "MRM_GET_CONFIG_CONFIRM",
    0x1103: "MRM_CONTROL_CONFIRM",
    0x1104: "MRM_SERVER_CONNECT_CONFIRM",
    0x1105: "MRM_SERVER_DISCONNECT_CONFIRM",
    0x1106: "MRM_SET_FILTER_CONFIG_CONFIRM",
    0x1107: "MRM_GET_FILTER_CONFIG_CONFIRM",
    0xF001: "MRM_GET_STATUSINFO_REQUEST",
    0xF002: "MRM_REBOOT_REQUEST",
    0xF003: "MRM_SET_OPMODE_REQUEST",
    0xF005: "MRM_SET_SLEEPMODE_REQUEST",
    0xF006: "MRM_GET_SLEEPMODE_REQUEST",
    0xF101: "MRM_GET_STATUSINFO_CONFIRM",
    0xF102: "MRM_REBOOT_CONFIRM",
    0xF103: "MRM_SET_OPMODE_CONFIRM",
    0xF105: "MRM_SET_SLEEPMODE_CONFIRM",
    0xF106: "MRM_GET_SLEEPMODE_CONFIRM",
    0xF201: "MRM_SCAN_INFO",
    0xF202: "MRM_READY_INFO",
    0xF10C: "MRM_GENERROR"
}


def resolve_name(id: str) -> int:
    """Resolves a packet name to an ID
        Args:
            id (str): The name to resolve
        Returns:
            The ID of the packet
    """

    # convert this into an id
    for key in message_types:
        if message_types[key] == id:
            return key
    raise ValueError("Invalid Message Type!")


def get_outgoing(id: int or str) -> dict:
    """Gets the outgoing packet data for a given ID
        Args:
            id (int or str): The ID of the packet to get
        Returns:
            The outgoing packet data
    """

    if isinstance(id, str):
        id = resolve_name(id)

    if id not in outgoing_func_bank:
        raise ValueError("Invalid Message Type!")

    return outgoing_func_bank[id]


def get_incoming(id: int or str) -> callable:
    """Gets the incoming packet data for a given ID
        Args:
            id (int or str): The ID of the packet to get
        Returns:
            The incoming packet data
    """

    if isinstance(id, str):
        id = resolve_name(id)

    if id not in incoming_func_bank:
        raise ValueError("Invalid Message Type!")

    return incoming_func_bank[id]
