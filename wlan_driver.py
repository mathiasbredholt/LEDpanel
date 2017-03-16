import network
import socket

TYPETAG_INT = 105
TYPETAG_STR = 115


def setup(settings):
    wlan = network.WLAN(network.STA_IF)  # Create station interface
    wlan.active(True)

    ap = network.WLAN(network.AP_IF)  # Create access-point interface
    ap.active(False)

    found_networks = wlan.scan()
    for wifi in settings["wifi"]:
        if any(wifi["ssid"] == x[0].decode("utf-8") for x in found_networks):
            # Known network found. Connecting as client.
            wlan.connect(wifi["ssid"], wifi["password"])
            wlan.ifconfig(
                (settings["ip"], "255.255.255.0", "192.168.1.1", "192.168.1.1"))
            return wlan

    # XYZ network not found. Creating access point.
    wlan.active(False)
    ap.active(True)
    ap.config(essid="XYZ", password="xyzxyzxyz")
    ap.ifconfig((settings["ip"], "255.255.255.0",
                 "192.168.1.1", "192.168.1.1"))
    return ap


def create_socket(device):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((device.ifconfig()[0], 1811))
    return sock


def parse_osc(msg):
    # convert to bytearray and add , character to end
    address = ""
    index = 0
    from_typetags = bytearray()
    typetags = []
    data = []
    # separate message into bytesarray for each argument
    for i, x in enumerate(msg):
        if x == 44:  # , separator
            address = msg[0:i].decode().rstrip("\0")
            index = i + 1
            from_typetags = msg[index:]
    for x in from_typetags:
        if x == TYPETAG_INT:
            typetags.append(TYPETAG_INT)
        elif x == TYPETAG_STR:
            typetags.append(TYPETAG_STR)
        else:
            index = index + 4 - (index % 4)
            break
        index = index + 1
    for x in typetags:
        if x == TYPETAG_INT:
            data.append(
                (msg[index] << 24) | (msg[index + 1] << 16) | (
                    msg[index + 2] << 8) | msg[index + 3]
            )
            index = index + 4
    return address, data
