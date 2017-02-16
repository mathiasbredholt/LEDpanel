# XYZ STROBE LIGHTS // BY MATHIAS BREDHOLT

import time
import machine
import socket
import colorsys
import network

_settings = {}

MAX_DUTY = 900

TYPETAG_INT = 105
TYPETAG_STR = 115

# Which program is running
STATIC = 0
STROBE = 1
AUDIO = 2

_mode = STATIC

_strobe_timer1 = machine.Timer(-1)
_strobe_timer2 = machine.Timer(-1)
_strobe_timer3 = machine.Timer(-1)

_rainbow_timer = machine.Timer(-1)
_rainbow_hue = 0.0

BLACK = (0, 0, 0, 0)


_rgbw = BLACK
_rgbw_next = BLACK


def load_settings():
    global _settings
    with open("settings", "r") as f:
        data = f.readlines()
        _settings["ip"] = data[0].strip()
        _settings["wifi"] = []
        for wifi in data[1:]:
            ssid, password = wifi.split(";")
            _settings["wifi"].append(
                {"ssid": ssid, "password": password.strip("\n")})
        f.close()


def save_settings():
    with open("settings", "w") as f:
        f.write(_settings["ip"])
        for wifi in _settings["wifi"]:
            f.write("\n" + wifi["ssid"] + ";" + wifi["password"])
        f.close()


def init_xyz():
    global _pwms
    load_settings()

    p5 = machine.Pin(5, machine.Pin.OUT)  # D1, White
    pwm5 = machine.PWM(p5)
    pwm5.freq(1000)
    pwm5.duty(1023)

    p4 = machine.Pin(4, machine.Pin.OUT)  # D2, Blue
    pwm4 = machine.PWM(p4)
    pwm4.freq(1000)
    pwm4.duty(1023)

    p0 = machine.Pin(0, machine.Pin.OUT)  # D3, Green
    pwm0 = machine.PWM(p0)
    pwm0.freq(1000)
    pwm0.duty(1023)

    p2 = machine.Pin(2, machine.Pin.OUT)  # D4, Red
    pwm2 = machine.PWM(p2)
    pwm2.freq(1000)
    pwm2.duty(1023)

    _pwms = (pwm2, pwm0, pwm4, pwm5)


def create_socket(device):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((device.ifconfig()[0], 1811))
    return s


def receive_osc(s):
    while 1:
        addr, data = parse_osc(s.recv(64))
        if addr == "/rgbw":
            set_color(data)
        elif addr == "/on":
            leds_toggle(True)
        elif addr == "/off":
            leds_toggle(False)
        elif addr == "/strobe_on":
            strobe_toggle(True, data[0], data[1])
        elif addr == "/strobe_off":
            strobe_toggle(False, 0, 0)
        elif addr == "/rainbow_on":
            rainbow_toggle(True, data[0], data[1], data[2], data[3])
        elif addr == "/rainbow_off":
            rainbow_toggle(False, 0)
        elif addr == "/manual":
            set_color(data)
            leds_toggle(True)


def set_leds(rgbw=None):
    global _rgbw
    if rgbw is None:
        rgbw = _rgbw_next
    for i, x in enumerate(_pwms):
        if rgbw[i] != _rgbw[i]:
            x.duty(1023 - min(int((rgbw[i] / 255)**2 * 1023), MAX_DUTY))
    if rgbw != _rgbw:
        _rgbw = rgbw


def leds_toggle(val):
    global _mode
    # Turn leds on/off with fixed color
    if val:
        _mode = STATIC
        set_leds()
    else:
        if _mode != STATIC:
            _mode = STATIC
            strobe_toggle(False, 0, 0)
        rainbow_toggle(False)
        set_leds(BLACK)


def set_color(rgbw):
    # Color calibration here
    global _rgbw_next
    _rgbw_next = tuple(rgbw)


def strobe_toggle(val, period=100, duty=10):
    global _mode
    _strobe_timer1.deinit()
    _strobe_timer2.deinit()
    _strobe_timer3.deinit()
    if val:
        _mode = STROBE
        _strobe_timer1.init(period=period, mode=machine.Timer.PERIODIC,
                            callback=lambda t: strobe_do(True))
        _strobe_timer2.init(period=int(period * duty / 100), mode=machine.Timer.ONE_SHOT, callback=lambda t:
                            _strobe_timer3.init(period=period, mode=machine.Timer.PERIODIC, callback=lambda t: strobe_do(False)))
    else:
        leds_toggle(False)


def strobe_do(val):
    if val:
        set_leds()
    else:
        set_leds(BLACK)


def rainbow_toggle(val, period=500, step=1, sat=255, bright=255):
    _rainbow_timer.deinit()
    if val:
        _rainbow_timer.init(
            period=period, mode=machine.Timer.PERIODIC, callback=lambda t: rainbow_do(step, sat, bright))


def rainbow_do(step, sat, bright):
    global _rainbow_hue
    if _rainbow_hue > 1:
        _rainbow_hue = 0
    r, g, b = colorsys.hsv_to_rgb(_rainbow_hue, sat / 255, bright / 255)
    _rainbow_hue = _rainbow_hue + step / 255
    set_color((int(r * 255), int(g * 255), int(b * 255), _rgbw_next[3]))
    if _mode == STATIC:
        set_leds()


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


def setup_wifi():
    wlan = network.WLAN(network.STA_IF)  # Create station interface
    wlan.active(True)

    ap = network.WLAN(network.AP_IF)  # Create access-point interface
    ap.active(False)

    found_networks = wlan.scan()
    for wifi in _settings["wifi"]:
        if any(wifi["ssid"] == x[0].decode("utf-8") for x in found_networks):
            # Known network found. Connecting as client.
            wlan.connect(wifi["ssid"], wifi["password"])
            wlan.ifconfig(
                (_settings["ip"], "255.255.255.0", "192.168.1.1", "192.168.1.1"))
            return wlan

    # XYZ network not found. Creating access point.
    wlan.active(False)
    ap.active(True)
    ap.config(essid="XYZ", password="xyzxyzxyz")
    ap.ifconfig((_settings["ip"], "255.255.255.0",
                 "192.168.1.1", "192.168.1.1"))
    return ap
