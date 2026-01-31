 

from motorControlTest import *
from sensor_func_test import *

# Encoders match your working file :contentReference[oaicite:3]{index=3}
LEFT_ENC_CLK  = 19
LEFT_ENC_DATA = 22
RIGHT_ENC_CLK  = 15
RIGHT_ENC_DATA = 16

# Motor PWM pins:
# Your file shows one motor on pins 20/21 :contentReference[oaicite:4]{index=4}
LEFT_IN1_PIN = 20
LEFT_IN2_PIN = 21

# TODO: set these to your actual motor-2 driver pins
RIGHT_IN1_PIN = 18
RIGHT_IN2_PIN = 17

def make_robot():
    encL = PIOEncoder(sm_id=0, clk_pin=LEFT_ENC_CLK, data_pin=LEFT_ENC_DATA)
    encR = PIOEncoder(sm_id=1, clk_pin=RIGHT_ENC_CLK, data_pin=RIGHT_ENC_DATA)

    mL = Motor(LEFT_IN1_PIN, LEFT_IN2_PIN, pwm_freq=2000, invert=False)
    mR = Motor(RIGHT_IN1_PIN, RIGHT_IN2_PIN, pwm_freq=2000, invert=False)

    bot = DiffDrive(
        left_motor=mL, right_motor=mR,
        left_enc=encL, right_enc=encR,
        wheel_diam_cm=4.5,
        wheelbase_cm=9.6,
#         ticks_per_wheel_rev=830,  
    )
    return bot

# Example usage:
# bot = make_robot()
# bot.move_forward_18cm()
# bot.rotate_left_90deg()
# bot.rotate_right_90deg()
# bot.rotate_180deg()

if __name__ == "__main__":
    bot = make_robot()
#     bot.move_forward_18cm()
#     bot.move_forward_cm(18)
#     bot.rotate_left_deg(90.3)

#     bot.rotate_left_90deg()
#     bot.estimate_ticks_per_rev()
    
    
#     Sensing test
#     tof_setup()
#     print_3_sensor_readings()

#     emec_scl = Pin(5)
#     emec_sda = Pin(4)
#     i2c = I2C(0, sda=emec_sda, scl=emec_scl, freq=400_000)
# 
#     tof = TOFMultiplexer(i2c=i2c, mux_addr=0x70, channels=(0, 1, 2))
# 
#     d_left  = tof.get_distance_mm(0)
#     d_mid   = tof.get_distance_mm(1)
#     d_right = tof.get_distance_mm(2)
# 
#     print(d_left, d_mid, d_right)
# 
#     # Or all at once:
#     print(tof.get_all_distances_mm())

    tof = TOFMultiplexer(bus=0, sda_pin=4, scl_pin=5, channels=(0,1,2))

    print(tof.get_distance_mm(0))
    print(tof.get_distance_mm(1))
    print(tof.get_distance_mm(2))