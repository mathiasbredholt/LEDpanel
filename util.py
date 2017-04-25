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
