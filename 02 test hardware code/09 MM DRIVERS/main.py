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
        
#     print("starting next tests")
#     
#     def test2():
#         print('Yo')
#         time.sleep(0.1)
#     
#     button_exit_loop(mm,test2)
    
    print("actual pid tests fr this time...")
    
    def pid_test1(test_power):        
        # 1 second forward
        count = 0
        encoder_m1_0, encoder_m2_0 = mm.get_encoders()
        time.sleep(0.01)
            
        while not count > 100:     
            mm.drive_forward(power=test_power)
            
            encoder_m1, encoder_m2 = mm.get_encoders()
            print("motor1: ", encoder_m1, "| motor2: ", encoder_m2)
            
            v1 = (encoder_m1 - encoder_m1_0)/0.1
            v2 = (encoder_m2 - encoder_m2_0)/0.1
            encoder_m1_0 = encoder_m1
            encoder_m2_0 = encoder_m2
#             print("velocity1: ", v1, "| velocity2: ", v2)
            
            count = count + 1
            
            time.sleep(0.01)
        
        time.sleep(1)
        count = 0    
        while not count > 100:
            mm.drive_backward(power=test_power)
            
            encoder_m1, encoder_m2 = mm.get_encoders()
            print("motor1: ", encoder_m1, "| motor2: ", encoder_m2)
            count = count + 1
            
            v1 = (encoder_m1 - encoder_m1_0)/0.1
            v2 = (encoder_m2 - encoder_m2_0)/0.1
            encoder_m1_0 = encoder_m1
            encoder_m2_0 = encoder_m2
#             print("velocity1: ", v1, "| velocity2: ", v2)
            
            time.sleep(0.01)
    
    test_power = 254
    pid_test1(test_power)
    
    test_power = 120
    pid_test1(test_power)

        
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
