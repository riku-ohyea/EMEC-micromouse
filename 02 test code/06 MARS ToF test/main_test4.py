from machine import Pin, I2C
import time
from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from PiicoDev_SSD1306 import *


emec_scl = Pin(5)
emec_sda = Pin(4)


# Pico I2C0 defaults often used in examples:
i2c = I2C(0, sda=emec_sda, scl=emec_scl, freq=400_000)

emec_scl = Pin(5)
emec_sda = Pin(4)


MUX_ADDR = 0x70

def mux_select(channel: int):
    # Select exactly one channel (0-7)
    i2c.writeto(MUX_ADDR, bytes([1 << channel]))

# Create 3 sensor objects (they all use address 0x29, separated by mux channels)
mux_select(0)
s0 = PiicoDev_VL53L1X(bus=0, sda=emec_sda, scl=emec_scl)

mux_select(1)
s1 = PiicoDev_VL53L1X(bus=0, sda=emec_sda, scl=emec_scl)

mux_select(2)
s2 = PiicoDev_VL53L1X(bus=0, sda=emec_sda, scl=emec_scl)

while True:
    mux_select(0)
    d0 = s0.read()  # mm (PiicoDev VL53L1X returns distance)
    mux_select(1)
    d1 = s1.read()
    mux_select(2)
    d2 = s2.read()

    print("ch0:", d0, "mm | ch1:", d1, "mm | ch2:", d2, "mm")
#     time.sleep(0.1)
    sleep_ms(50)

