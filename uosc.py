import ustruct

TYPETAG_INT = 'i'
TYPETAG_STR = 's'
TYPETAG_FLOAT = 'f'


def is_bundle(datagram):
    if datagram[0:7] == b'#bundle':
        return True
    return False


def parse_osc_string(datagram):
    i = 0
    while datagram[i] != 0:
        i = i + 1
    s = datagram[0:i].decode()
    return s, i + 4 - (i & 0x03)


def parse_osc_int(datagram):
    return ustruct.unpack('>i', datagram)[0]


def parse_osc_float(datagram):
    return ustruct.unpack('>f', datagram)[0]


def parse_timestamp(datagram):
    sec, frac = ustruct.unpack('>ll', datagram)
    if (sec == 0) and (frac <= 1):
        return 0.0
    else:
        return int(sec) + float(frac / 1e9)


class OSCBundle():
    """OSC bundle class """

    def __init__(self, datagram):
        self.timestamp = parse_timestamp(datagram[8:16])
        self.data = []

        print(datagram)

        idx = 16
        while len(datagram) - idx > 0:
            size = ustruct.unpack('>i', datagram[idx:idx + 4])[0]
            idx = idx + 4

            if is_bundle(datagram[idx:idx + size]):
                self.data.append(OSCBundle(datagram[idx:idx + size]))
            else:
                self.data.append(OSCMessage(datagram[idx:idx + size]))

            idx = idx + size


class OSCMessage():
    """OSC message class"""

    def __init__(self, datagram):
        """
        Parses raw UDP datagram into a simple OSC message
        addr is a string of the type '/manual' or '/do/cool/stuff'
        data is a variable sized list containing 32 bit integers [ int, int, int, ...]
        """
        self.data = []
        idx = 0

        self.address, l = parse_osc_string(datagram)
        idx = idx + l

        s, l = parse_osc_string(datagram[idx:])
        self.typetags = s[1:]  # remove ',' character
        idx = idx + l

        for tt in self.typetags:
            if tt == TYPETAG_INT:
                self.data.append(parse_osc_int(datagram[idx:idx + 4]))
                idx = idx + 4
            elif tt == TYPETAG_FLOAT:
                self.data.append(parse_osc_float(datagram[idx:idx + 4]))
                idx = idx + 4
            elif tt == TYPETAG_STR:
                s, l = parse_osc_string(datagram[idx:])
                self.data.append(s)
                idx = idx + l
