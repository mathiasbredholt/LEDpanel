# This file is run on startup by MicroPython bootloader

import machine
import webrepl
import wlan_driver
import pwm_driver
import mic_driver

# Initialize global settings dictionary
_settings = {}


def load_settings(settings):
    '''
    Parses the settings file
    '''
    with open("settings", "r") as f:
        data = f.readlines()
        settings["ip"] = data[0].strip()
        settings["wifi"] = []
        for wifi in data[1:]:
            ssid, password = wifi.split(";")
            settings["wifi"].append(
                {"ssid": ssid, "password": password.strip("\n")})
        f.close()


def save_settings(settings):
    '''
    Saves new settings to the settings file
    '''
    with open("settings", "w") as f:
        f.write(settings["ip"])
        for wifi in settings["wifi"]:
            f.write("\n" + wifi["ssid"] + ";" + wifi["password"])
        f.close()

load_settings(_settings)

# Setup WiFi
wlan = wlan_driver.setup(_settings)

# Start WebREPL
webrepl.start()

# Setup PCA9685 library and
# intialize channel 1 to 25% duty cycle
pwm = pwm_driver.setup()
pwm_driver.rgbw(pwm, 1024, 0, 0, 0)

# Create UDP socket
sock = wlan_driver.create_socket(wlan)

# Main application loop
while 1:
    # Call sock.recv which is blocking
    # and parse into a OSC message
    addr, data = wlan_driver.parse_osc(sock.recv(64))
    if addr == "/rgbw":
        pwm_driver.rgbw(pwm, data[0], data[1], data[2], data[3])
    # Add new messages here
    # elif addr == "/matightass"
    #   pwm.duty(chan (0-15), val (0-4095))
