#!/usr/bin/env python3
import API

# Directions
N, E, S, W = 0, 1, 2, 3
DIRS = [(-1,0),(0,1),(1,0),(0,-1)]  # (dx, dy)
DIR_BITS = [1, 2, 4, 8]
OPPOSITE = [2, 3, 0, 1]

WIDTH = API.mazeWidth()   # Should be 5
HEIGHT = API.mazeHeight() # Should be 5

# Center tile for 5x5 maze
CENTER_TILE = (2, 2)

# Maze state
walls = [[0]*HEIGHT for _ in range(WIDTH)]
visited = [[False]*HEIGHT for _ in range(WIDTH)]
steps_map = [[-1]*HEIGHT for _ in range(WIDTH)]

# Mouse state
x, y = 0, 0  # Starting at top-left corner
dir = N
step_count = 0

# ---------------- Helper functions ----------------

def in_bounds(nx, ny):
    return 0 <= nx < WIDTH and 0 <= ny < HEIGHT

def sense_walls():
    """Update walls at current position"""
    global walls
    for offset, check in [(0, API.wallFront), (-1, API.wallLeft), (1, API.wallRight)]:
        d = (dir + offset) % 4
        if check():
            walls[x][y] |= DIR_BITS[d]
            nx, ny = x + DIRS[d][0], y + DIRS[d][1]
            if in_bounds(nx, ny):
                walls[nx][ny] |= DIR_BITS[OPPOSITE[d]]

def rotate_left():
    global dir
    API.turnLeft()
    dir = (dir - 1) % 4

def rotate_right():
    global dir
    API.turnRight()
    dir = (dir + 1) % 4

def move_forward():
    """Move one tile forward and stop if at center"""
    global x, y, step_count
    API.moveForward()
    x += DIRS[dir][0]
    y += DIRS[dir][1]
    step_count += 1
    visited[x][y] = True
    steps_map[x][y] = step_count
    # Stop immediately if center reached
    if (x, y) == CENTER_TILE:
        exit()

# ---------------- Main Left-Hand Wall Loop ----------------

visited[x][y] = True
steps_map[x][y] = step_count
sense_walls()

while True:
    if not API.wallLeft():
        rotate_left()
        move_forward()
    elif not API.wallFront():
        move_forward()
    elif not API.wallRight():
        rotate_right()
        move_forward()
    else:
        rotate_right()
        rotate_right()
        move_forward()
    sense_walls()
