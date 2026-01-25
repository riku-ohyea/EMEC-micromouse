from micromouse import Micromouse
from machine import Pin, I2C

import time
from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from PiicoDev_SSD1306 import *

mm = Micromouse()
mm.motor_1.invert_motor()

if __name__ == "__main__":

    mm.drive_stop()