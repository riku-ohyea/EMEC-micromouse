"""
Testing MARS robot compatibility with PiicoDev sensors
"""

# Piico dev libs
from PiicoDev_SSD1306 import *
from PiicoDev_VL53L1X import PiicoDev_VL53L1X

# MARS micrmouse libs
from micromouse import Micromouse

from machine import Pin
import time

emec_scl = Pin(5)
emec_sda = Pin(4)


mm = Micromouse()

display = create_PiicoDev_SSD1306(bus=0, sda=emec_sda, scl=emec_scl)
distSensor = PiicoDev_VL53L1X(bus=0, sda=emec_sda, scl=emec_scl)

counter = 1
# 
# 
if __name__ == "__main__":
    while True:
        # Read distance
        dist = distSensor.read() # read the distance in millimetres
        print(str(dist) + " mm") # convert the number to a string and print
        
        display.fill(0)
        display.text("PiicoDev",30,20, 1)
        display.text(str(dist)+"mm",50,35, 1)
        display.show()
        counter = counter + 1
        sleep_ms(100)
