# Backup function for 3x sensor reading

from machine import Pin, I2C
import time
from PiicoDev_VL53L1X import PiicoDev_VL53L1X

class TOFMultiplexer:
    def __init__(self, bus: int, sda_pin: int, scl_pin: int, mux_addr=0x70, channels=(0,1,2)):
        self.bus = bus
        self.sda = Pin(sda_pin)
        self.scl = Pin(scl_pin)

        # create ONE I2C object for mux control (optional but convenient)
        self.i2c = I2C(self.bus, sda=self.sda, scl=self.scl, freq=100_000)

        self.mux_addr = mux_addr
        self.channels = list(channels)

        self.wallBoundaryDist = 60

        self.sensors = []
        for ch in self.channels:
            self.mux_select(ch)
            time.sleep_ms(20)  # let mux + sensor settle

            # retry init a few times
            sensor = None
            for _ in range(3):
                try:
                    sensor = PiicoDev_VL53L1X(bus=self.bus, sda=self.sda, scl=self.scl, freq=100_000)
                    break
                except OSError:
                    time.sleep_ms(50)
                    self.mux_disable_all()
                    time.sleep_ms(10)
                    self.mux_select(ch)
                    time.sleep_ms(20)

            if sensor is None:
                raise RuntimeError("Failed to init TOF on mux channel {}".format(ch))

            self.sensors.append(sensor)

        self.mux_disable_all()

    def mux_select(self, channel: int):
        self.i2c.writeto(self.mux_addr, bytes([1 << channel]))

    def mux_disable_all(self):
        self.i2c.writeto(self.mux_addr, b"\x00")

    def get_distance_mm(self, index: int) -> int:
        ch = self.channels[index]
        self.mux_select(ch)
        return self.sensors[index].read()
