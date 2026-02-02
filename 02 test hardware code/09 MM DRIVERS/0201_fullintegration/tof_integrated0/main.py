import API

try:
    from collections import deque
except ImportError:
    from ucollections import deque

from Direction import Direction
from Maze import Maze
from Mouse import Mouse

import sys

from PIDMotorControl import *
from TOFSensors import *

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

# def log(string):
    # Might have to change to print statements on micropython/pi pico

# Unreachable infinite cost
INF = 10**9


def main():

    bot = make_robot()

    tof = TOFMultiplexer(bus=0, sda_pin=4, scl_pin=5, channels=(0,1,2))

    print(tof.get_distance_mm(0))
    print(tof.get_distance_mm(1))
    print(tof.get_distance_mm(2))

    #     bot.move_forward_cm(18)
#     bot.rotate_left_deg(90.3)


    maze = Maze(API.mazeWidth(), API.mazeHeight())
    mouse = Mouse(0, 0, Direction.NORTH)

    width = API.mazeWidth()
    height = API.mazeHeight()

    # Initial cost grid (computed with currently-known walls: none yet)
    costs = computeFloodFillCosts(maze)

    # drawCosts(costs, width, height)

    while not maze.inCenter(mouse.getPosition()):
        updateWalls(maze, mouse, tof)

        # Recompute whenever we learn new walls (simple + robust)
        costs = computeFloodFillCosts(maze)

        # drawCosts(costs, width, height)

        # optional: highlight current & accessible neighbors
        # paintLocalDebug(maze, mouse, costs)

        # optional: detailed console debug
        # logStep(maze, mouse, costs)

        moveOneCellFloodFill(maze, mouse, costs)

    print("Maze should be solved...?")


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
#         ticks_per_wheel_rev=830,  # set on the DiffDrive instead
    )
    return bot

def updateWalls(maze, mouse, tof):
    pos = mouse.getPosition()
    d = mouse.getDirection()

    if API.wallFront(tof = tof):
        setWallBothSides(maze, pos, d)

    if API.wallLeft(tof = tof):
        setWallBothSides(maze, pos, Direction.turnLeft(d))

    if API.wallRight(tof = tof):
        setWallBothSides(maze, pos, Direction.turnRight(d))


def moveOneCellFloodFill(maze, mouse, costs):
    current = mouse.getPosition()

    # If we're in a local minimum (no neighbor has lower cost),
    # recompute costs again (in case the newest walls changed the wavefront).
    if isLocalMinimum(maze, current, costs):
        costs = computeFloodFillCosts(maze)

    next_cell = chooseNextCellByCost(maze, mouse, costs)

    if next_cell is None:
        # Extremely defensive fallback: recompute and try once more.
        costs = computeFloodFillCosts(maze)
        next_cell = chooseNextCellByCost(maze, mouse, costs)

    if next_cell is None:
        # If still none, we cannot move anywhere (surrounded by known walls).
        
        print("No accessible moves from current cell based on known walls.")
        return

    turnAndMove(mouse, current, next_cell)


def chooseNextCellByCost(maze, mouse, costs):
    current = mouse.getPosition()
    cur_dir = mouse.getDirection()

    # Priority order when costs tie: forward > right > left > backward
    dirs_priority = [
        cur_dir,
        Direction.turnRight(cur_dir),
        Direction.turnLeft(cur_dir),
        Direction.turnAround(cur_dir),
    ]

    best = None
    best_cost = INF

    for d in dirs_priority:
        nb = getNeighbor(current, d)

        if not maze.contains(nb):
            continue
        if maze.getWall(current, d):
            continue

        c = costs.get(nb, INF)
        if c < best_cost:
            best_cost = c
            best = nb
        # If c == best_cost, we do nothing because we already traverse
        # in the required priority order.

    return best


def isLocalMinimum(maze, cell, costs):
    """Return True if no accessible neighbor has a strictly lower cost."""
    cell_cost = costs.get(cell, INF)

    for d in Direction.ALL:  # micropython-compatible list
        nb = getNeighbor(cell, d)
        if not maze.contains(nb):
            continue
        if maze.getWall(cell, d):
            continue
        if costs.get(nb, INF) < cell_cost:
            return False

    return True


def computeFloodFillCosts(maze):
    """
    Flood-fill / wavefront from goal (center).
    Uses ONLY known walls in `maze.getWall(...)`.
    Unknown walls are treated as open (because they are not set yet).
    Will this work on micropython??
    """
    width = API.mazeWidth()
    height = API.mazeHeight()

    # Cost storage as dict[(x,y)] -> int (works without needing Maze internals)
    costs = {(x, y): INF for x in range(width) for y in range(height)}

    # Initialize queue with ALL center cells (works for even-width mazes too)
    q = collections.deque()
    for x in range(width):
        for y in range(height):
            if maze.inCenter((x, y)):
                costs[(x, y)] = 0
                q.append((x, y))

    # BFS wavefront expansion
    while q:
        cell = q.popleft()
        base = costs[cell]

        for d in Direction.ALL:
            nb = getNeighbor(cell, d)

            if not maze.contains(nb):
                continue

            # IMPORTANT: wall check from 'cell' to 'nb'
            # if maze.getWall(cell, d):
            #     continue

            if edgeBlocked(maze, cell, d):
                continue


            new_cost = base + 1
            if new_cost < costs[nb]:
                costs[nb] = new_cost
                q.append(nb)

    return costs


def turnAndMove(mouse, current, next_cell):
    currentX, currentY = current
    nextX, nextY = next_cell

    if nextX < currentX:
        nextDirection = Direction.WEST
    elif nextX > currentX:
        nextDirection = Direction.EAST
    elif nextY < currentY:
        nextDirection = Direction.SOUTH
    else:
        nextDirection = Direction.NORTH

    currentDirection = mouse.getDirection()

    if Direction.turnLeft(currentDirection) == nextDirection:
        mouse.turnLeft()
    elif Direction.turnRight(currentDirection) == nextDirection:
        mouse.turnRight()
    elif currentDirection != nextDirection:
        mouse.turnAround()

    mouse.moveForward()


def getNeighbor(current, direction):
    x, y = current
    if direction == Direction.NORTH:
        y += 1
    if direction == Direction.EAST:
        x += 1
    if direction == Direction.SOUTH:
        y -= 1
    if direction == Direction.WEST:
        x -= 1
    return (x, y)

# Helper functions

def drawCosts(costs, width, height):
    """
    Draw the cost grid as text. MMS limits text length to 10 chars. :contentReference[oaicite:1]{index=1}
    """



def paintLocalDebug(maze, mouse, costs):
    """
    Colors current cell and accessible neighbors.
    """


def logStep(maze, mouse, costs):
    """
    Prints current cost + each neighbor cost + whether blocked.
    This is the fastest way to find why you got stuck.
    """
    # cur = mouse.getPosition()
    # cur_dir = mouse.getDirection()
    # log(f"@ {cur} heading={cur_dir} cost={costs.get(cur, INF)}")

    # # show in tie-break order (forward > right > left > back)
    # dirs = [
    #     ("F", cur_dir),
    #     ("R", Direction.turnRight(cur_dir)),
    #     ("L", Direction.turnLeft(cur_dir)),
    #     ("B", Direction.turnAround(cur_dir)),
    # ]

    # for label, d in dirs:
    #     nb = getNeighbor(cur, d)
    #     if not maze.contains(nb):
    #         log(f"  {label}: {nb} OOB")
    #         continue
    #     w = maze.getWall(cur, d)
    #     c = costs.get(nb, INF)
    #     log(f"  {label}: {nb} wall={w} cost={c}")

def setWallBothSides(maze, cell, direction):
    maze.setWall(cell, direction)

    nb = getNeighbor(cell, direction)
    if maze.contains(nb):
        maze.setWall(nb, Direction.turnAround(direction))

def edgeBlocked(maze, cell, direction):
    nb = getNeighbor(cell, direction)
    if not maze.contains(nb):
        return True
    return (
        maze.getWall(cell, direction)
        or maze.getWall(nb, Direction.turnAround(direction))
    )

if __name__ == "__main__":
    main()
