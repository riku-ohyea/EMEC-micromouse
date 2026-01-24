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

        encoder_m1 = mm.motor_1.encoder_read()
        encoder_m2 = mm.motor_2.encoder_read()
        
        print("motor1: ", encoder_m1, "| motor2: ", encoder_m2)
        time.sleep(0.05)
        
        # aprox 1065-1076 counts full turn
        
        button_bool = mm.get_button()
        print("| button: ", button_bool)

        