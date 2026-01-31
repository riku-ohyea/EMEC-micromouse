import API
import sys
from math import *

def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()

def main():
    log("Running...")
    API.setColor(0, 0, "R")
    maxwidth = API.mazeWidth()
    maxheight = API.mazeHeight()
    # print(maxheight, " | ", maxwidth)
    log(f"{maxheight} | {maxwidth}")
    centre_height = floor(maxheight/2)

    # API.setText(0, 0, "start")

    while True:
        if not API.wallLeft():
            API.turnLeft()
        while API.wallFront():
            API.turnRight()
        API.moveForward()

if __name__ == "__main__":
    main()
