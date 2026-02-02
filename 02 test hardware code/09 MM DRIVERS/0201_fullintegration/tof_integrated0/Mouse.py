

# Mouse.py (edits only)
import API
from Direction import Direction

# Class object for where the mouse is in the (internal) maze.

class Mouse:
    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.d = d

    def getPosition(self):
        return (self.x, self.y)

    def getDirection(self):
        return self.d

    def turnLeft(self):
        API.turnLeft()
        self.d = Direction.turnLeft(self.d)

    def turnRight(self):
        API.turnRight()
        self.d = Direction.turnRight(self.d)

    def turnAround(self):
        self.turnRight()
        self.turnRight()

    def moveForward(self):
        API.moveForward()
        if self.d == Direction.NORTH:
            self.y += 1
        elif self.d == Direction.EAST:
            self.x += 1
        elif self.d == Direction.SOUTH:
            self.y -= 1
        elif self.d == Direction.WEST:
            self.x -= 1
