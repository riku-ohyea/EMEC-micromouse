

# Direction.py (MicroPython-friendly)
class Direction:
    # Use small ints (fast + compact)
    NORTH = 0
    EAST  = 1
    SOUTH = 2
    WEST  = 3

    # for-loops like: for d in Direction.ALL:
    ALL = (NORTH, EAST, SOUTH, WEST)

    # Optional: keep your existing "value" idea for API.setWall(...)
    VALUE = {
        NORTH: "n",
        EAST:  "e",
        SOUTH: "s",
        WEST:  "w",
    }

    @staticmethod
    def turnLeft(d):
        return (d - 1) & 3

    @staticmethod
    def turnRight(d):
        return (d + 1) & 3
    
    @staticmethod
    def turnAround(d):
        return (d + 2) & 3
