# This file is run on startup by MicroPython bootloader

import machine
import webrepl
import wlan_driver
import pwm_driver
import mic_driver
import uosc

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

time = 0
timer1 = None


def timer_callback(t):
    global time
    time = time + 1
    print(time)

# Main application loop
while 1:
    # Call sock.recv which is blocking
    # and parse into a OSC message

    datagram = sock.recv(64)

    if uosc.is_bundle(datagram):
        msg = uosc.OSCBundle(datagram)
        timetag = msg.timetag

        print(msg.data[0])
        if type(msg.data[0]) is uosc.OSCMessage:
            msg = msg.data[0]
            if msg.address == "/time":
                global time
                time = timetag[0]
                timer1.init(period=1000, mode=machine.Timer.PERIODIC,
                            callback=timer_callback)

    else:
        msg = uosc.OSCMessage(datagram)

        if msg.address == "/rgbw":
            pwm_driver.rgbw(pwm, msg.data[0], msg.data[
                1], msg.data[2], msg.data[3])

    # msg = wlan_driver.OSCMessage(sock.recv(64))
    # if msg.address == "/rgbw":
    #
    # else:
    #     if msg.type == wlan_driver.OSCBUNDLE:
    #         print(msg.address, msg.data, msg.timetag)
    # Add new messages here
    # elif address == "/matightass"
    #   pwm.duty(chan (0-15), val (0-4095))
