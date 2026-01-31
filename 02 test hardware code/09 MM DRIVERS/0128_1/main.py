from rp2 import PIO, StateMachine, asm_pio
from machine import Pin, PWM, Timer
import micropython
import utime
import math


class QuadratureDecoder:
    """
    Track rotary encoder position using programmable IO controller (PIO)
    """

    def __init__(self, pin_a, pin_b):
        self.sm = StateMachine(1, self._encoder, freq=125_000_000, in_base=pin_b, jmp_pin=pin_a)

        # Reset counter
        self.sm.put(0)
        self.sm.exec("pull()")
        self.sm.exec("out(x, 32)")

        # Start PIO
        self.sm.active(1)

    @micropython.viper
    def read(self) -> int:
        """
        Get the current position of the encoder
        """
        self.sm.exec("in_(x, 32)")
        x = self.sm.get()

        # Convert unsigned to signed
        # There doesn't seem to be a native way to get this from PIO
        if x & 0x80000000:
            x -= 0xFFFFFFFF
            
        return int(x)
        
    @asm_pio(autopush=True, push_thresh=32)
    def _encoder():
        """
        SPDX-FileCopyrightText: 2022 Jamon Terrell <github@jamonterrell.com>
        SPDX-License-Identifier: MIT
        https://github.com/jamon/pi-pico-pio-quadrature-encoder/
        """
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


class Motor():
    def __init__(self):
        # self.encoder = QuadratureDecoder(Pin(2), Pin(3))
        self.encoder = QuadratureDecoder(Pin(19), Pin(22))

        # self.pwm = PWM(Pin(13), freq=20000, duty_u16=0)
        # self.fwd = Pin(15, mode=Pin.OUT, value=0)
        # self.rev = Pin(14, mode=Pin.OUT, value=0)
        self.pwm_m1 = PWM(Pin(21), freq = 2000)
        self.pwm_m2 = PWM(Pin(20), freq = 2000)
        
        self.max_out = 65535
    
        self.read = self.encoder.read
        
    def brake(self):
        # self.pwm.duty_u16(0)
        # self.rev.off()
        # self.fwd.off()
        self.pwm_m1.duty_u16(0)
        self.pwm_m2.duty_u16(0)
        
    # def freewheel(self):
    #     self.pwm.duty_u16(0)
    #     self.rev.on()
    #     self.fwd.on()
                
    def set_speed(self, percent: float):
        clamped = max(min(100, percent), -100) / 100.0
        output = int(clamped * self.max_out)

        if output > -100 and output < 100:
            # Stop if the value is small enough to not do anything
            self.brake()
        elif output > 0:
            # self.rev.off()
            # self.fwd.on()
            self.pwm_m1.duty_u16(abs(output))
            self.pwm_m2.duty_u16(0)
        else:
            # self.fwd.off()
            # self.rev.on()
            self.pwm_m2.duty_u16(abs(output))
            self.pwm_m1.duty_u16(0)

        # self.pwm.duty_u16(abs(output))


class PidMotor(Motor):
    def __init__(self, Kp, Ki, Kd):
        super().__init__()

        # PID settings
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        # PID state
        self.integral = 0
        self.last_error = 0
        self.last_update = utime.ticks_us()

        # Inputs
        self.target = 0
        self._smoothed_target = 0
        self.enable = False
        
        self._timer = Timer(period=1, mode=Timer.PERIODIC, callback=self._update)
        
    @micropython.native
    def _update(self, t):
        pos = self.encoder.read()

        now = utime.ticks_us()
        dt = (now - self.last_update)/1e6
        
        self._smoothed_target += (self.target - self._smoothed_target) * 0.02

        if self.enable:
            error = self._smoothed_target - pos
            self.integral = self.integral + dt * error
            derivative = (error - self.last_error)/dt
            output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        else:
            error = 0
            self.integral = 0
            output = 0
            
        if not self.enable:
            self.brake()
        else:
            self.set_speed(output)

        self.last_update = now
        self.last_error = error    


def cleanup_pios():
    """ Free any allocated PIOs from a previous interactive run """
    for i in range(6):
        try:
            rp2.PIO(i).remove_program()
        except:
            continue


# Motor sensing and control
cleanup_pios()
motor = PidMotor(
    Kp=0.8, # Proportional
    Ki=1.8, # Integral
    Kd=0.0, # Derivative
)

motor.max_out = 65535

# PID Demo
count = 0
motor.target = 120
# motor.enable = True
# 
# start = utime.ticks_us()
# 
# while True:
#     now = utime.ticks_us() - start
#     motor.target = motor.target * -1
#     utime.sleep(1)
#
motor.enable = False
while True:
    print(motor.encoder.read())
    utime.sleep_ms(100)