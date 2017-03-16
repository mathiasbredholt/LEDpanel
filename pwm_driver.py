import machine
import pca9685


def setup():
    i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
    pwm = pca9685.PCA9685(i2c)
    pwm.freq(1600)
    return pwm


def rgbw(pwm, r, g, b, w):
    pwm.duty(0, r)
    pwm.duty(1, g)
    pwm.duty(2, b)
    pwm.duty(3, w)
