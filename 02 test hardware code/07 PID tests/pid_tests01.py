"""
This file is provided as a sample of basic initialisation and working for
"plug-and-play" of the drivers, but is expected to be altered to implement
system control algorithms.
"""
from micromouse import Micromouse
from machine import Pin, I2C

import time
from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from PiicoDev_SSD1306 import *

mm = Micromouse()


if __name__ == "__main__":
    while True:
#         mm.led_green_set(0)

        encoder_values = mm.Motor.encoder_read()
        print(encoder_values)
        time.sleep(0.05)

        