# encoder_sweep.py
import time
from micromouse import Micromouse

def reset_encoders(mm):
    # Rotary library supports reset(); Motor wrapper doesn't expose it, so we reach in.
    mm.motor_1._encoder.reset()
    mm.motor_2._encoder.reset()

def log_once(mm, pwm_cmd, last_e1, last_e2):
    e1, e2 = mm.get_encoders()
    de1, de2 = e1 - last_e1, e2 - last_e2
    print(f"PWM={pwm_cmd:>4}  enc1={e1:>8} (d{de1:>6})  enc2={e2:>8} (d{de2:>6})")
    return e1, e2

def hold_and_sample(mm, pwm_cmd, hold_s=0.8, sample_period_s=0.05):
    
    # test kick start
    
    # Apply power
    if pwm_cmd > 0:
        mm.drive_forward(255)
        mm.drive_forward(pwm_cmd)
    elif pwm_cmd < 0:
        mm.drive_backward(-255)
        mm.drive_backward(-pwm_cmd)
    else:
        mm.drive_stop()

    # Sample encoder deltas during the hold
    t_end = time.ticks_add(time.ticks_ms(), int(hold_s * 1000))
    last_e1, last_e2 = mm.get_encoders()
    while time.ticks_diff(t_end, time.ticks_ms()) > 0:
        time.sleep(sample_period_s)
        last_e1, last_e2 = log_once(mm, pwm_cmd, last_e1, last_e2)

def sweep(mm, start, stop, step, hold_s=0.8, sample_period_s=0.05, pause_s=0.3):
    if step == 0:
        raise ValueError("step cannot be 0")
    if (stop - start) * step < 0:
        step = -step

    for pwm in range(start, stop + (1 if step > 0 else -1), step):
        print("\n---")
        hold_and_sample(mm, pwm, hold_s=hold_s, sample_period_s=sample_period_s)
        mm.drive_stop()
        time.sleep(pause_s)

def main():
    mm = Micromouse()

    print("Reset encoders and start sweep.")
    reset_encoders(mm)
    time.sleep(0.5)

#     # Forward sweep 0..255
#     print("\n=== FORWARD SWEEP ===")
#     sweep(mm, start=0, stop=100, step=10, hold_s=0.8, sample_period_s=0.05, pause_s=1)
# 
#     # Backward sweep 0..-255
#     print("\n=== BACKWARD SWEEP ===")
#     reset_encoders(mm)
#     sweep(mm, start=0, stop=-100, step=-10, hold_s=0.8, sample_period_s=0.05, pause_s=1)

#     Sweep from neg to pos
    print("\n=== NEGATIVE TO POSITIVE ===")
    sweep(mm, start=-120, stop=120, step=10, hold_s=4, sample_period_s=0.5, pause_s=1)

    mm.drive_stop()
    print("\nDone.")

# main()
