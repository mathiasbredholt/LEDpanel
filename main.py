import machine
import webrepl
import wlan_driver
import pwm_driver
import mic_driver

_settings = {}


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

load_settings()

wlan = wlan_driver.setup(_settings)
webrepl.start()

pwm = pwm_driver.setup()
pwm_driver.rgbw(pwm, 1024, 0, 0, 0)

sock = wlan_driver.create_socket(wlan)

while True:
    addr, data = wlan_driver.parse_osc(sock.recv(64))
    if addr == "/rgbw":
        pwm_driver.rgbw(pwm, data[0], data[1], data[2], data[3])
