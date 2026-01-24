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
mm.motor_1.invert_motor()


if __name__ == "__main__":
#     while True:
# #         mm.led_green_set(0)
# 
#         encoder_m1 = mm.motor_1.encoder_read()
#         encoder_m2 = mm.motor_2.encoder_read()
#         
#         print("motor1: ", encoder_m1, "| motor2: ", encoder_m2)
#         time.sleep(0.05)
#         
#         # aprox 1065-1076 counts full turn
#         
#         button_bool = mm.get_button()
# #         print("| button: ", button_bool)
#         if button_bool:
#             # break out of loop for testing purposes
#             break
#         
#     # Continue test from here
#     # 18cm aprox 1296, 1246-1250
# #     print("")
# #     time.sleep(5)
#     
#     print("exited encoder print loop.")
#     print("waiting 5 seconds ....")
#     time.sleep(5)
#     print("push button to enter next tests")
#     
#     while True:
#         button_bool = mm.get_button()
#         if button_bool:
#             print("entering next tests...")
#             time.sleep(5)
#             break
#     
#     print("entered next test")
#     
#     # Test run 18cm
#     step_dist = 180
#     
#     step_rate = 1250
#     
#     target_step = round(step_dist * step_rate /step_dist)
#     print("targ step", target_step)
#     
#     init_encoder_m1 = mm.motor_1.encoder_read()
#     init_encoder_m2 = mm.motor_2.encoder_read()
#     
#     step_count_m1 = init_encoder_m1
#     step_count_m2 = init_encoder_m2
#     
#     target_step_m1 = init_encoder_m1 + target_step
#     target_step_m2 = init_encoder_m2 + target_step
#     
#     print(step_count_m1, "| ", target_step_m1, "| ", step_count_m2, "| ", target_step_m2, "| ")
#     
#     while (step_count_m1 < target_step_m1) or (step_count_m2 < target_step_m2):
#         step_count_m1 = mm.motor_1.encoder_read()
#         step_count_m2 = mm.motor_2.encoder_read()
#         print(step_count_m1, "| ", target_step_m1, "| ", step_count_m2, "| ", target_step_m2, "| ")
#         
#         mm.drive_forward(power = round(50))
#         print("motor1: ", step_count_m1, "| motor2: ", step_count_m2)
#         mm.drive_forward(power = round(50))
#         
#         button_bool = mm.get_button()
#         if button_bool:
#             print("entering next tests...")
#             break
#         
#         time.sleep(0.05)
#         
#     mm.drive_stop()

    mm.drive_forward(power = 60)
    time.sleep(2)
    mm.drive_stop()
