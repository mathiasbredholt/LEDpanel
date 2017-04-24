import network
import socket


def setup(settings):
    """
    Connects to known WiFi networks and returns nework device
    If none of the known WiFi networks are found
    creates WiFi hotspot XYZ with password xyzxyzxyz
    """
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
    """
    Initializes UDP socket with given device returned from setup
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((device.ifconfig()[0], 1811))
    return sock
