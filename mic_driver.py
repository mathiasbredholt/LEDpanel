from machine import ADC
from machine import Timer
import pwm_driver
import math

_adc = ADC(0)
_tim = Timer(-1)
_buffer = [0] * 16
_index = 0


def start_mic_control(pwm):
    _tim.init(period=5, mode=Timer.PERIODIC,
              callback=lambda t: read_from_mic(pwm))


def stop_mic_control():
    _tim.deinit()


def read_from_mic(pwm):
    global _buffer
    global _index

    _buffer[_index] = (_adc.read() - 512) ** 2
    _index = _index + 1

    if _index == 16:
        _index = 0

    energy = max(0, min(4095, int(sum(_buffer)) >> 5))
    # pwm_driver.rgbw(pwm, 0, energy, 0, 0)
