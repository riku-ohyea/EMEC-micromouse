# SPDX-FileCopyrightText: 2022 Jamon Terrell <github@jamonterrell.com>
# SPDX-License-Identifier: MIT

# self.encoder = QuadratureDecoder(Pin(19), Pin(22))
# motor 2 with these pins -> motor_2 = Motor(17, 18, 15, 16)
# 
from rp2 import PIO, StateMachine, asm_pio
from machine import Pin, PWM
import utime
@asm_pio(autopush=True, push_thresh=32)
def encoder():
    label("start")
    wait(0, pin, 0)         # Wait for CLK to go low
    jmp(pin, "WAIT_HIGH")   # if Data is low
    mov(x, invert(x))           # Increment X
    jmp(x_dec, "nop1")
    label("nop1")
    mov(x, invert(x))
    label("WAIT_HIGH")      # else
    jmp(x_dec, "nop2")          # Decrement X
    label("nop2")
    
    wait(1, pin, 0)         # Wait for CLK to go high
    jmp(pin, "WAIT_LOW")    # if Data is low
    jmp(x_dec, "nop3")          # Decrement X
    label("nop3")
    
    label("WAIT_LOW")       # else
    mov(x, invert(x))           # Increment X
    jmp(x_dec, "nop4")
    label("nop4")
    mov(x, invert(x))
    wrap()

    
sm1 = StateMachine(
    0,
    encoder,
    freq=125_000_000,
    in_base=Pin(22,Pin.IN, Pin.PULL_UP),
    jmp_pin=Pin(19,Pin.IN, Pin.PULL_UP)
    )
sm1.active(1)

sm2 = StateMachine(
    1,
    encoder,
    freq=125_000_000,
    in_base=Pin(16,Pin.IN, Pin.PULL_UP),
    jmp_pin=Pin(15,Pin.IN, Pin.PULL_UP)
    )
sm2.active(1)

# ----------
# Define motors

m1_1 = PWM(Pin(20), freq = 2000)
m1_2 = PWM(Pin(21), freq = 2000)

duration_ms = 1000
start = utime.ticks_ms()

# Example: Run a loop for 2.5 seconds
duration_seconds = 2500
start_time = utime.ticks_ms() # Get the current time in seconds

if __name__ == "__main__":

    while utime.ticks_ms() - start_time < duration_seconds:
        # Your loop code here
        print(f"Loop running, time left: {duration_seconds - (utime.ticks_ms() - start_time)} miliseconds")
        utime.sleep(0.05) # Sleep briefly to prevent the loop from hogging the CPU

    print("Loop finished after 2.5 seconds.")
    
    print("loading next process...")
    utime.sleep(1)
        
    utime.sleep(0.05)
    sm1.exec("in_(x, 32)")
    m1_enc = sm1.get()
    sm2.exec("in_(x, 32)")
    m2_enc = sm2.get()
    print(m1_enc, "|",m2_enc)
    
    target_count = 1400
    sm1.exec("in_(x, 32)")
    current_count = sm1.get()
    target_count = (current_count+target_count)
    print(target_count)
    
    while current_count < target_count:
        print("entered loop")
        
        m1_1.duty_u16(100*257)
        m1_2.duty_u16(0)
        
        sm1.rx_fifo()
        sm1.exec("in_(x, 32)")
        current_count = sm1.get()
        print(current_count)
        
        utime.sleep(0.05)
        
    print("exited loop")
    m1_1.duty_u16(0)
    m1_2.duty_u16(0)
        
    
# --------------------------------------------------------
# Testing other encoder code

# from micromouse import Micromouse
# from machine import Pin, I2C
# 
# import time
# import utime
# from PiicoDev_VL53L1X import PiicoDev_VL53L1X
# from PiicoDev_SSD1306 import *
# 
# from encoder_sweep import *
# 
# mm = Micromouse()
# mm.motor_2.invert_motor()
# mm.drive_stop()
# 
# if __name__ == "__main__":
#     while(True):
#         utime.sleep(0.05)
#         m1_enc, m2_enc = mm.get_encoders()
#         print(m1_enc, "|",m2_enc)
#     
#     
#     
# mm.drive_stop()

