# Testing stepcounts on encoder. Seems to be counting oddly?
"""
Testing stepcounts on encoder. Seems to be counting oddly?
1. test if counting is consistent at different speeds
2. Single motor PID

Move towards PID control based on step counts on encoder
1. move specified distance
2. turn specified rotation
"""

from micromouse import Micromouse
from machine import Pin, I2C

import time
from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from PiicoDev_SSD1306 import *

mm = Micromouse()
mm.motor_1.invert_motor()
mm.drive_stop()

def test_encoder_counts:
    encoder_m1, encoder_m2 = mm.get_encoders()
    print("motor1: ", encoder_m1, "| motor2: ", encoder_m2)
    time.sleep(0.1)
    
    while not mm.get_button():
        encoder_m1, encoder_m2 = mm.get_encoders()
        print("motor1: ", encoder_m1, "| motor2: ", encoder_m2)
        time.sleep(0.1)
    

if __name__ == "__main__":
    
    test_encoder_counts()

    mm.drive_stop()