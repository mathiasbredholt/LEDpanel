Download with
git clone --recursive

Upload firmware following this guide
- https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html

The firmware bin file is included in this repository.

Install ampy for uploading files to ESP
- https://github.com/adafruit/ampy

Put following files in the root folder of ESP
- main.py
- pwm_driver.py
- mic_driver.py
- wlan_driver.py
- uosc.py
- externals/pca9685/pca9685.py
- settings

Connect PCA9685
- SCL -> GPIO5 (D1 on Lolin dev board)
- SDA -> GPIO4 (D2 on Lolin dev board)

After reboot it should work.