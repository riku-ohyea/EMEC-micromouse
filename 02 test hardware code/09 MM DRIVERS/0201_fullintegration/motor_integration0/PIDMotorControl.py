# MicroPython (RP2040 / Pico)
# - PIO-based quadrature-ish counter from your working example
# - Differential-drive PID for distance + heading (encoder difference)
#
# Update motor PWM pins to match your hardware!

from rp2 import StateMachine, asm_pio
from machine import Pin, PWM
import utime
import math
import struct

# ----------------------------
# PIO encoder (from your file)
# ----------------------------
@asm_pio(autopush=True, push_thresh=32)
def encoder():
    label("start")
    wait(0, pin, 0)         # Wait for CLK to go low
    jmp(pin, "WAIT_HIGH")   # if Data is low
    mov(x, invert(x))       # Increment X (using invert trick)
    jmp(x_dec, "nop1")
    label("nop1")
    mov(x, invert(x))
    label("WAIT_HIGH")      # else
    jmp(x_dec, "nop2")      # Decrement X
    label("nop2")

    wait(1, pin, 0)         # Wait for CLK to go high
    jmp(pin, "WAIT_LOW")    # if Data is low
    jmp(x_dec, "nop3")      # Decrement X
    label("nop3")

    label("WAIT_LOW")       # else
    mov(x, invert(x))       # Increment X
    jmp(x_dec, "nop4")
    label("nop4")
    mov(x, invert(x))
    wrap()

def u32_to_i32(v):
    # StateMachine.get() returns unsigned; convert to signed 32-bit
    return struct.unpack("!i", struct.pack("!I", v & 0xFFFFFFFF))[0]

class PIOEncoder:
    def __init__(self, sm_id, clk_pin, data_pin):
        # Your example:
        # in_base = Pin(data_pin)
        # jmp_pin = Pin(clk_pin)
        self.sm = StateMachine(
            sm_id,
            encoder,
            freq=125_000_000,
            in_base=Pin(data_pin, Pin.IN, Pin.PULL_UP),
            jmp_pin=Pin(clk_pin, Pin.IN, Pin.PULL_UP),
        )
        self.sm.active(1)
        self._last = self.read()

    def read(self):
        # Grab current X register value (as in your example)
        self.sm.exec("in_(x, 32)")
        return u32_to_i32(self.sm.get())

    def delta(self):
        cur = self.read()
        d = cur - self._last
        self._last = cur
        return d

# ----------------------------
# Motor driver (2 PWM pins)
# ----------------------------
class Motor:
    def __init__(self, in1_pin, in2_pin, pwm_freq=2000, invert=False):
        # self.in1 = PWM(Pin(in1_pin), freq=pwm_freq)
        # self.in2 = PWM(Pin(in2_pin), freq=pwm_freq)
        self.in1 = PWM(Pin(in1_pin))
        self.in2 = PWM(Pin(in2_pin))
        self.in1.freq(pwm_freq)
        self.in2.freq(pwm_freq)
        self.invert = invert
        self.set(0)

    def set(self, power):
        """
        power: -1.0 .. +1.0
        """
        if self.invert:
            power = -power

        power = max(-1.0, min(1.0, power))

        if power >= 0:
            duty = int(power * 65535)
            self.in1.duty_u16(duty)
            self.in2.duty_u16(0)
        else:
            duty = int((-power) * 65535)
            self.in1.duty_u16(0)
            self.in2.duty_u16(duty)

    def stop(self):
        self.in1.duty_u16(0)
        self.in2.duty_u16(0)

# ----------------------------
# PID controller
# ----------------------------
class PID:
    def __init__(self, kp, ki, kd, out_min=-1.0, out_max=1.0, i_limit=1.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.out_min = out_min
        self.out_max = out_max
        self.i_limit = abs(i_limit)
        self.i = 0.0
        self.prev_err = 0.0
        self.prev_t = utime.ticks_ms()

    def reset(self):
        self.i = 0.0
        self.prev_err = 0.0
        self.prev_t = utime.ticks_ms()

    def update(self, err, dt):
        # Integrator with clamp (anti-windup)
        self.i += err * dt
        if self.i > self.i_limit:
            self.i = self.i_limit
        elif self.i < -self.i_limit:
            self.i = -self.i_limit

        d = (err - self.prev_err) / dt if dt > 0 else 0.0
        self.prev_err = err

        out = self.kp * err + self.ki * self.i + self.kd * d
        if out > self.out_max:
            out = self.out_max
        elif out < self.out_min:
            out = self.out_min
        return out

# ----------------------------
# Differential drive controller
# ----------------------------
class DiffDrive:
    def __init__(self, left_motor, right_motor, left_enc, right_enc,
                 wheel_diam_cm=4.5, wheelbase_cm=9.6,
                 ticks_per_wheel_rev=1075):

        self.L = left_motor
        self.R = right_motor
        self.eL = left_enc
        self.eR = right_enc

        self.wheel_diam_cm = wheel_diam_cm
        self.wheelbase_cm = wheelbase_cm
        self.ticks_per_wheel_rev = ticks_per_wheel_rev

        self.wheel_circ_cm = math.pi * wheel_diam_cm
        self.ticks_per_cm = ticks_per_wheel_rev / self.wheel_circ_cm

        # PID gains (STARTING POINTS — you will tune)
        # Distance PID drives average encoder to target.
        self.pid_dist = PID(kp=0.0048, ki=0.0000, kd=0.000045, out_min=-0.3, out_max=0.3, i_limit=0.5)
        # Heading PID drives difference encoder to 0 (straight) or to target (turn).
        self.pid_head = PID(kp=0.00285, ki=0.0000, kd=0.000030, out_min=-0.2, out_max=0.2, i_limit=0.5)

        # Motion loop params
        self.dt = 0.003  #  Hz
        self.min_power = 0.325  # helps overcome stiction; tune for your robot
        self.done_band_ticks = 7  # stop when within this many ticks
        self.max_time_s = 7.0  # safety timeout per command; adjust as needed

    def _apply_deadband(self, u):
        if u == 0:
            return 0
        if 0 < u < self.min_power:
            return self.min_power
        if -self.min_power < u < 0:
            return -self.min_power
        return u

    def reset_pids(self):
        self.pid_dist.reset()
        self.pid_head.reset()

    def stop(self):
        self.L.stop()
        self.R.stop()

    def cm_to_ticks(self, cm):
        return int(cm * self.ticks_per_cm)

    def deg_to_turn_ticks(self, deg):
        # In-place turn: each wheel travels arc length = (wheelbase/2) * theta
        theta = math.radians(deg)
        arc_cm = (self.wheelbase_cm / 2.0) * theta
        return self.cm_to_ticks(arc_cm)

    def _get_counts(self):
        # absolute counts
        cL = self.eL.read()
        cR = self.eR.read()
        return cL, cR

    def _run_to_targets(self, target_avg_ticks, target_diff_ticks):
        """
        target_avg_ticks: desired average wheel ticks (forward/back)
        target_diff_ticks: desired (left - right) tick difference (turn)
        """
        self.reset_pids()

        # Capture starting counts
        startL, startR = self._get_counts()

        t0 = utime.ticks_ms()

        while True:
            now = utime.ticks_ms()
            elapsed_s = utime.ticks_diff(now, t0) / 1000.0
            if elapsed_s > self.max_time_s:
                break

            # Current relative ticks from start
            curL, curR = self._get_counts()
            relL = curL - startL
            relR = curR - startR

            avg = (relL + relR) / 2.0
            diff = (relL - relR) * 1.0  # left - right

            err_avg = target_avg_ticks - avg
            err_diff = target_diff_ticks - diff

            # Stop condition: both errors small
            if abs(err_avg) < self.done_band_ticks and abs(err_diff) < self.done_band_ticks:
                break

            # PID outputs
            u_dist = self.pid_dist.update(err_avg, self.dt)
            u_head = self.pid_head.update(err_diff, self.dt)

            # Mix: distance + heading correction
            uL = u_dist + u_head
            uR = u_dist - u_head

            # Clamp and deadband
            uL = max(-1.0, min(1.0, uL))
            uR = max(-1.0, min(1.0, uR))
            uL = self._apply_deadband(uL)
            uR = self._apply_deadband(uR)

            self.L.set(uL)
            self.R.set(uR)

            utime.sleep(self.dt)

        self.stop()

    # ----------------------------
    # Public motion primitives
    # ----------------------------
    def move_forward_cm(self, cm):
        ticks = self.cm_to_ticks(cm)
        self._run_to_targets(target_avg_ticks=ticks, target_diff_ticks=0)

    def rotate_left_deg(self, deg):
        turn_ticks = self.deg_to_turn_ticks(deg)
        # For left rotation: left wheel backward, right wheel forward
        # That corresponds to positive (left - right) diff target?
        # If sign is reversed on your robot, flip the sign here.
        self._run_to_targets(target_avg_ticks=0, target_diff_ticks=-2 * turn_ticks)

    def rotate_right_deg(self, deg):
        turn_ticks = self.deg_to_turn_ticks(deg)
        self._run_to_targets(target_avg_ticks=0, target_diff_ticks=+2 * turn_ticks)

    # Convenience wrappers you asked for:
    def move_forward_18cm(self):
        self.move_forward_cm(18.0)

    def rotate_left_90deg(self):
        self.rotate_left_deg(90.0)

    def rotate_right_90deg(self):
        self.rotate_right_deg(90.0)

    def rotate_180deg(self):
        self.rotate_left_deg(180.0)

    # ----------------------------
    # Simple calibration helper
    # ----------------------------
    def estimate_ticks_per_rev(self, seconds=0.98, power=0.6):
        """
        Rough check: spin both wheels forward and measure encoder delta.
        Not perfect (wheel slip), but helps sanity-check the tick scale.
        """
        cL0, cR0 = self._get_counts()
        self.L.set(power)
        self.R.set(power)
        utime.sleep(seconds)
        self.stop()
        cL1, cR1 = self._get_counts()
        print("Encoder delta L:", cL1 - cL0, "R:", cR1 - cR0)
