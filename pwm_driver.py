# This module requires the Adafruit PCA9685 library
# Put tpca9585.py in root folder of ESP8266

import machine
import pca9685


def setup():
    '''
    Setup the interface for PCA9685
    Returns Adafruit PCA9685 object 
    '''
    i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
    pwm = pca9685.PCA9685(i2c)
    pwm.freq(1600)
    return pwm


def rgbw(pwm, r, g, b, w):
    '''
    Call with PWM object returned from setup
    r, g, b, w must be integers between 0-4095
    '''
    pwm.duty(0, r)
    pwm.duty(1, g)
    pwm.duty(2, b)
    pwm.duty(3, w)
