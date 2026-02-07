from machine import Pin, PWM
import time
import colorsys
import board
import busio
import adafruit_vl6180x
from adafruit_apds9960 import colorutility
from adafruit_apds9960.apds9960 import APDS9960



red_gate_colour = 0
red_bandwidth = 0.1
red_saturation_min = 0.5
red_value_min = 0.002

green_gate_colour = 0.3333333
green_bandwidth = 0.1
green_saturation_min = 0.5
green_value_min = 0.002

MAX_COLOR = 65535


i2c = busio.I2C(board.GP1, board.GP0)


#1150 ticks for 17.5 cm
ticks_per_cm = 66


AIN1 = Pin(11, Pin.OUT)
AIN2 = Pin(19, Pin.OUT)

BIN1=Pin(10, Pin.OUT)
BIN2=Pin(21, Pin.OUT)

PWMA_PIN=Pin(18, Pin.OUT)
PWMB_PIN=Pin(22, Pin.OUT)

PWMA = PWM(PWMA_PIN, freq=1500, duty_u16=35000)
PWMB = PWM(PWMB_PIN, freq=1500, duty_u16=35000)



STBY = Pin(20, Pin.OUT)

#encoder motor a
EC1A=Pin(26, Pin.IN, Pin.PULL_UP)
EC2A=Pin(27,Pin.IN, Pin.PULL_UP)

ecA_position=0

#encoder motor b
EC1B=Pin(16, Pin.IN, Pin.PULL_UP)
EC2B=Pin(17,Pin.IN, Pin.PULL_UP)

ecB_position=0

def create_sensor(i2c, address):
    sensor = adafruit_vl6180x.VL6180X(i2c)
    sensor.set_address(i2c, address)
    sensor.start_range_continuous(period = 100)
    
    return sensor




def setup_sensors():
    shut_forward = Pin(13, Pin.OUT)
    shut_left = Pin(12, Pin.OUT)
    shut_right = Pin(28, Pin.OUT)

    shut_forward.off()
    shut_left.off()
    shut_right.off()

    shut_pins = [shut_left, shut_forward, shut_right]

    sensors = [None, None, None]

    num_sensors = 3

    for i in range(num_sensors):
        shut_pins[i].on()
        time.sleep(0.5)
        sensors[i] = create_sensor(i2c, 0x29 + 2*(3-i))
    sensors.append(APDS9960(i2c))
    sensors[3].enable_color = True
    sensors[3].color_integration_time = 72
    return sensors

def get_walls():
    code = 0b0000
    if sensors[0].range < 100:
        code |= 1<<3
    if sensors[1].range < 100:
        code |= 1<<0
    if sensors[2].range < 100:
        code |= 1<<1
    return code

def get_gate():
    apds = sensors[3]
    r,g,b,c = apds.color_data
    while not apds.color_data_ready:
        time.sleep(0.005)
    r,g,b,c = apds.color_data

    hsv = colorsys.rgb_to_hsv(r/MAX_COLOR, g/MAX_COLOR, b/MAX_COLOR)

    if ((hsv[0] > green_gate_colour - green_bandwidth) and (hsv[0] < green_gate_colour + green_bandwidth) and
    (hsv[1] > green_saturation_min) and (hsv[2] > green_value_min)):
        return 1
    elif ((hsv[0] > red_gate_colour - red_bandwidth) and (hsv[0] < red_gate_colour + red_bandwidth) and
    (hsv[1] > red_saturation_min) and (hsv[2] > red_value_min)):
        return -1
    else:
        return 0

def ecA_increment(pin):
    global ecA_position
    bool_ecA=EC2A.value()
    #if rising edge detected on encoder 2nd channel, increase rotational position counter
    if bool_ecA:
        #rotating forwards because channel 2 triggers after channel 1
        ecA_position-=1
    else:
        #rotating backwards because channel 2 has triggered first
        ecA_position+=1
    # print("MOTOR A:")
    # print(ecA_position)

#establish interrupt for motor A        
EC1A.irq(trigger=Pin.IRQ_FALLING, handler=ecA_increment)


def ecB_increment(pin):
    global ecB_position
    bool_ecB=EC1B.value()
    #if rising edge detected on encoder 2nd channel, increase rotational position counter
    if bool_ecB:
        #rotating forwards because channel 2 triggers after channel 1
        ecB_position-=1
    else:
        #rotating backwards because channel 2 has triggered first
        ecB_position+=1
    # print("MOTOR B:")
    # print(ecB_position)

#establish interrupt for motor B
EC2B.irq(trigger=Pin.IRQ_FALLING, handler=ecB_increment)


def cm_to_tick(cm):
    return int(ticks_per_cm * cm)

def forward():
    STBY.low()
    AIN1.high()
    AIN2.low()
    BIN1.high()
    BIN2.low()
    global ecA_position
    global ecB_position
    thresh_A = cm_to_tick(18)
    thresh_B = cm_to_tick(18)
    while ecA_position<thresh_A and ecB_position<thresh_B:
        STBY.high()
    STBY.low()
    time.sleep(0.5)
    reset_encoders()

def rotate(turn_amount):
    #positive turn to the right, negative to the left
    if turn_amount < 0:
            turn_left()
    elif turn_amount > 0:
            turn_right()
        

def move_backward():
    STBY.low()
    AIN1.low()
    AIN2.high()
    BIN1.low()
    BIN2.high()
    global ecA_position
    global ecB_position
    thresh_A = cm_to_tick(18)
    thresh_B = cm_to_tick(18)
    while ecA_position>-thresh_A and ecB_position>-thresh_B:
        STBY.high()
    STBY.low()
    time.sleep(0.5)
    reset_encoders()
    
def turn_right():
    STBY.low()
    AIN1.low()
    AIN2.high()
    BIN1.high()
    BIN2.low()
    global ecA_position
    global ecB_position
    thresh_A = cm_to_tick(6.97)
    thresh_B = cm_to_tick(6.97)
    while ecA_position>-thresh_A and ecB_position<thresh_B:
        STBY.high()
    STBY.low()
    time.sleep(0.5)
    reset_encoders()

def turn_left():
    STBY.low()
    AIN2.low()
    AIN1.high()
    BIN2.high()
    BIN1.low()
    global ecA_position
    global ecB_position
    thresh_A = cm_to_tick(6.97)
    thresh_B = cm_to_tick(6.97)
    while ecA_position<thresh_A and ecB_position>-thresh_B:
        STBY.high()
    STBY.low()
    time.sleep(0.5)
    reset_encoders()


def bonk():
    STBY.low()
    AIN1.low()
    AIN2.high()
    BIN1.low()
    BIN2.high()
    global ecA_position
    global ecB_position
    thresh_A = cm_to_tick(6.5)
    thresh_B = cm_to_tick(6.5)
    while ecA_position>-thresh_A and ecB_position>-thresh_B:
        STBY.high()
    STBY.low()
    time.sleep(0.2)
    reset_encoders()
    AIN1.high()
    AIN2.low()
    BIN1.high()
    BIN2.low()
    thresh_A = cm_to_tick(3.6)
    thresh_B = cm_to_tick(3.6)
    while ecA_position<thresh_A and ecB_position<thresh_B:
        STBY.high()
    STBY.low()
    time.sleep(0.5)
    reset_encoders()


def reset_encoders():
    global ecA_position
    global ecB_position
    ecA_position=0
    ecB_position=0

PWMA.init()
PWMB.init()
sensors = setup_sensors()


if __name__ == "__main__":
    for count in range(4):
        forward()
    turn_right()
    forward()
    forward()
    turn_left()
    forward()
        
