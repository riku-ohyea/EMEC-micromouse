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

def test_encoder_counts():
    encoder_m1, encoder_m2 = mm.get_encoders()
    print("motor1: ", encoder_m1, "| motor2: ", encoder_m2)
    time.sleep(0.1)
    
    while not mm.get_button():
        encoder_m1, encoder_m2 = mm.get_encoders()
        print("motor1: ", encoder_m1, "| motor2: ", encoder_m2)
        time.sleep(0.1)
    else:
        print_exit_status()
        
    print("starting next tests")
    
    def test2():
        print('Yo')
        time.sleep(0.1)
    
    button_exit_loop(mm,test2)
    
    print("actual pid tests fr this time...")
    

        
def print_exit_status():
    print("Exiting while loop")
    print("Waiting 3 seconds....")
    print("3")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    time.sleep(1)
    print("Complete...")
    
def button_exit_loop(mm, test_function ):
    while not mm.get_button():
        test_function() # function to test
    else:
        print_exit_status()
        

if __name__ == "__main__":
    
    test_encoder_counts()

    mm.drive_stop()