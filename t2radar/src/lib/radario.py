# creates and manages socket connections
from lib.util import bytes_to_int, int_to_bytes
from lib.config import get_config
import socket

# create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# set timeout to 2 seconds
sock.settimeout(2)

cfg = get_config()

server_address = (cfg["net"]["ip"], cfg["net"]["port"])


def send_payload(msgtype: int, msgid: int, payload: bytes) -> int:
    """Constructs a packet and sends it to the radar.

    Args:
        msgtype (int): The message type.
        msgid (int): The message ID.
        payload (bytes): The payload.

    Returns:
        The number of bytes sent.
    """
    msgtype = int_to_bytes(msgtype, 16, False)
    msgid = int_to_bytes(msgid, 16, False)
    packet = msgtype + msgid + payload

    bytes_sent = sock.sendto(packet, server_address)

    return bytes_sent


def recv_payload() -> tuple[int, int, bytes]:
    """Receives a packet from the radar.

    Returns:
        The payload.
    """
    data, server = sock.recvfrom(4096)

    msgtype = bytes_to_int(data[0:2], False)
    msgid = bytes_to_int(data[2:4], False)

    return (msgtype, msgid, data[4:])


def killSocket():
    """Closes the socket."""
    sock.close()
