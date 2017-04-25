# This file is run on startup by MicroPython bootloader

import machine
import webrepl
import wlan_driver
import pwm_driver
import mic_driver
import uosc
import uheapq
import util


TIME_TOL = const(0.001)

# Initialize global settings dictionary
_settings = {}

util.load_settings(_settings)

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
pqueue = []


def timer_callback(t):
    global time
    time = time + TIME_TOL
    if abs(pqueue[0][0] - time) < TIME_TOL:
        msg = uheapq.heappop(pqueue)[1]
        if msg.address == "/rgbw":
            pwm_driver.rgbw(pwm, msg.data[0], msg.data[
                1], msg.data[2], msg.data[3])

# Main application loop
while 1:
    # Call sock.recv which is blocking
    datagram = sock.recv(64)

    if uosc.is_bundle(datagram):
        msg = uosc.OSCBundle(datagram)
        timestamp = msg.timestamp

        print(msg.data[0])
        if type(msg.data[0]) is uosc.OSCMessage:
            msg = msg.data[0]
            if msg.address == "/time":
                global time
                time = timestamp
                timer1.init(period=int(TIME_TOL * 1000), mode=machine.Timer.PERIODIC,
                            callback=timer_callback)
            else:
                uheapq.heappush(pqueue, (timestamp, msg))
    else:
        msg = uosc.OSCMessage(datagram)

        if msg.address == "/rgbw":
            pwm_driver.rgbw(pwm, msg.data[0], msg.data[
                1], msg.data[2], msg.data[3])
