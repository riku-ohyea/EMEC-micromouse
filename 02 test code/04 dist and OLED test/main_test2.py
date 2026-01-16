# Display distance readings on OLED

'''from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from time import sleep

distSensor = PiicoDev_VL53L1X()

while True:
    dist = distSensor.read() # read the distance in millimetres
    print(str(dist) + " mm") # convert the number to a string and print
    sleep(0.1)    
'''
    
# -----------------------

from PiicoDev_SSD1306 import *
from PiicoDev_VL53L1X import PiicoDev_VL53L1X


display = create_PiicoDev_SSD1306()
distSensor = PiicoDev_VL53L1X()

counter = 1

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
    

