from machine import ADC

_adc = ADC(0)


def read():
    return _adc.read << 2
