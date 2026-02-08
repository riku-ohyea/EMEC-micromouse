import sys

import utime

class MouseCrashedError(Exception):
    pass

def command(args, return_type=None):
    line = " ".join([str(x) for x in args]) + "\n"
    sys.stdout.write(line)
    sys.stdout.flush()
    if return_type:
        response = sys.stdin.readline().strip()
        if return_type == bool:
            return response == "true"
        return return_type(response)

# Adjust these on compday
def mazeWidth():
    mazeWidth = 9
    return mazeWidth

def mazeHeight():
    mazeHeight = 9
    return mazeHeight

def checkWall(wallCommand, half_steps_away=None, tof = None):
    # args = [wallCommand]
    # if half_steps_away is not None:
    #     args.append(half_steps_away)
    # return command(args, return_type=bool)
    if tof is None:
        raise ValueError("tof required")

    idx = None
    if wallCommand == "wallFront":
        idx = 1
    elif wallCommand == "wallLeft":
        idx = 0
    elif wallCommand == "wallRight":
        idx = 2
    else:
        return False

    d = tof.get_distance_mm(idx)
    if d is None:
        # Invalid read -> safest is "no wall" so maze logic doesn't crash
        return False

    return d < tof.wallBoundaryDist
    

def wallFront(half_steps_away=None, tof = None):
    if tof is None:
        raise ValueError("tof required")
    return checkWall("wallFront", tof = tof)

# def wallBack(half_steps_away=None):
#     return checkWall("wallBack", half_steps_away)

def wallLeft(half_steps_away=None, tof = None):
    if tof is None:
        raise ValueError("tof required")
    return checkWall("wallLeft", tof = tof)

def wallRight(half_steps_away=None, tof = None):
    if tof is None:
        raise ValueError("tof required")
    return checkWall("wallRight", tof = tof)


# Motor integration after getting the sensors to work

def moveForward(bot = None, tof=None):
    # args = ["moveForward"]
    # # Don't append distance argument unless explicitly specified, for
    # # backwards compatibility with older versions of the simulator
    # if distance is not None:
    #     args.append(distance)
    # response = command(args=args, return_type=str)
    # if response == "crash":
    #     raise MouseCrashedError()

    distance = 18.5

    print("Move forward one cell")
    if bot is None:
        raise ValueError("bot class object required")
    
    use_wall = False
    if tof is not None:
        # "two valid side walls from the cell its leaving"
        use_wall = wallLeft(tof=tof) and wallRight(tof=tof)
    
    # bot.move_forward_cm(distance)
    bot.move_forward_cm(distance, tof=tof, enable_wall_corr=use_wall, wall_corr_cm=7.0)
    print("We should be in the next cell now")

    # t0 = utime.ticks_ms()
    # while True:
    #         now = utime.ticks_ms()
    #         elapsed_s = utime.ticks_diff(now, t0) / 1000.0
    #         if elapsed_s > 5.0:
    #             break
    # print("We should be in the next cell now")


def turnRight(bot = None):
    angle = 89

    print("turning right")
    if bot is None:
        raise ValueError("bot class object required")
    
    bot.rotate_right_deg(angle)
#     print("We should be in the next cell now")

def turnAround(bot = None):
    angle = 176

    print("turning around")
    if bot is None:
        raise ValueError("bot class object required")
    
    bot.rotate_right_deg(angle)
#     print("We should be in the next cell now")

def turnLeft(bot = None):
    angle = 89

    print("turning left")
    if bot is None:
        raise ValueError("bot class object required")
    
    bot.rotate_left_deg(angle)
#     print("We should be in the next cell now")

# def bonk(bot = None, tof = None, distance_back_cm=-4.0, recenter_forward_cm=2.0):
# 
#     if bot is None:
#         raise ValueError("bot class object required")
#     
#     use_wall = False
#     if tof is not None:
#         # "two valid side walls from the cell its leaving"
#         use_wall = wallLeft(tof=tof) and wallRight(tof=tof)
#     
#     # Back into the wall, then come forward a touch to “recenter”
#     bot.move_forward_cm(distance_back_cm, tof=tof, enable_wall_corr=use_wall, wall_corr_cm=7.0)
#     bot.move_forward_cm(recenter_forward_cm, tof=tof, enable_wall_corr=use_wall, wall_corr_cm=7.0)

def bonk(bot=None, tof=None,
     back_power=-0.5,
     recenter_cm=2.0,
     max_back_ms=1000):

    if bot is None:
        raise ValueError("bot class object required")

    # 1) Back into the wall using open-loop until stall
    bot.drive_until_stall(back_power, back_power, max_ms=max_back_ms, stall_ms=100, min_delta_ticks=2)

    # 2) Come forward a touch (PID is fine here because you're not stalled anymore)
    use_wall = False
#     if tof is not None:
#         use_wall = wallLeft(tof=tof) and wallRight(tof=tof)

    bot.move_forward_cm(recenter_cm, tof=tof, enable_wall_corr=use_wall, wall_corr_cm=7.0)



# def setWall(x, y, direction):
#     command(args=["setWall", x, y, direction])

# def clearWall(x, y, direction):
#     command(args=["clearWall", x, y, direction])


