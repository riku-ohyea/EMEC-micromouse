

# Mouse.py (edits only)
import API
from Direction import Direction
import time

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

    def turnLeft(self, bot):
        API.turnLeft(bot)
        self.d = Direction.turnLeft(self.d)

    def turnRight(self, bot):
        API.turnRight(bot)
        self.d = Direction.turnRight(self.d)    

    def turnAround(self, bot):
#         print("first turn for 180deg")
#         self.turnRight(bot)
#         time.sleep_ms(500)
#         print("second turn")
#         self.turnRight(bot)
        
        API.turnAround(bot)
        self.d = Direction.turnAround(self.d) 

    def moveForward(self, bot, tof=None):
        # API.moveForward(bot)
        API.moveForward(bot, tof=tof)
        if self.d == Direction.NORTH:
            self.y += 1
        elif self.d == Direction.EAST:
            self.x += 1
        elif self.d == Direction.SOUTH:
            self.y -= 1
        elif self.d == Direction.WEST:
            self.x -= 1
