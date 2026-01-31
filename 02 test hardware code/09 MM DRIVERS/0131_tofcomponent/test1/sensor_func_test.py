# Backup function for 3x sensor reading

from machine import Pin, I2C
import time
from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from PiicoDev_SSD1306 import *


class TOFSensor():
    """
    
    """

    def __init__(self, emec_scl, emec_sda):
        """
        Initialises the member variables upon first creation.
        """
        self.emec_scl = Pin(5)
        self.emec_sda = Pin(4)
        
        # Pico I2C0 defaults often used in examples:
        self.i2c = I2C(0, sda=emec_sda, scl=emec_scl, freq=400_000)
        self.MUX_ADDR = 0x70
        
        # Create 3 sensor objects (they all use address 0x29, separated by mux channels)
        mux_select(0)
        self.s0 = PiicoDev_VL53L1X(bus=0, sda=emec_sda, scl=emec_scl)

        mux_select(1)
        self.s1 = PiicoDev_VL53L1X(bus=0, sda=emec_sda, scl=emec_scl)

        mux_select(2)
        self.s2 = PiicoDev_VL53L1X(bus=0, sda=emec_sda, scl=emec_scl)
        
        
    
    def mux_select(channel: int):
        # Select exactly one channel (0-7)
        i2c.writeto(MUX_ADDR, bytes([1 << channel]))

    def distance_read(self, sensor_number):
        """
        sensor_number:
        0 is left
        1 is centre
        2 is right
        """
        
        #     Will print sensor readings. But needs sleep time.
        mux_select(sensor_number)
        d0 = s0.read()  # mm (PiicoDev VL53L1X returns distance)
        return self.d0

