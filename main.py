import webrepl
import xyz
import machine

webrepl.start()

xyz.init_xyz()
wifi = xyz.setup_wifi()

# wlan = network.WLAN(network.STA_IF)  # create station interface
# wlan.active(False)       # activate the interface

# ap = network.WLAN(network.AP_IF)  # create access-point interface
# ap.active(True)         # activate the interface
# # set the ESSID of the access point
# ap.config(essid='XYZ', password='xyzxyzxyz')

# Wait for connection
while not wifi.isconnected():
    machine.idle()

s = xyz.create_socket(wifi)
# # Run main loop
xyz.receive_osc(s)
