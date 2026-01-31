@micropython.native # run this routine in native mode (lower level code)

import API
import collections

from Direction import Direction
from Maze import Maze
from Mouse import Mouse

def main():
    maze = Maze(API.mazeWidth(), API.mazeHeight())
    mouse = Mouse(0, 0, Direction.NORTH)
    while not maze.inCenter(mouse.getPosition()):
        updateWalls(maze, mouse)
        moveOneCell(maze, mouse)

def updateWalls(maze, mouse):
    position = mouse.getPosition()
    direction = mouse.getDirection()
    if API.wallFront():
        maze.setWall(position, direction)
    if API.wallLeft():
        maze.setWall(position, direction.turnLeft())
    if API.wallRight():
        maze.setWall(position, direction.turnRight()) 

def moveOneCell(maze, mouse):
    # Compute the next direction
    currentX, currentY = mouse.getPosition()
    nextX, nextY = getNextCell(maze, mouse)
    if nextX < currentX:
        nextDirection = Direction.WEST
    if nextY < currentY:
        nextDirection = Direction.SOUTH
    if nextX > currentX:
        nextDirection = Direction.EAST
    if nextY > currentY:
        nextDirection = Direction.NORTH

    # Turn and move to the next cell
    currentDirection = mouse.getDirection()
    if currentDirection.turnLeft() == nextDirection:
        mouse.turnLeft()
    elif currentDirection.turnRight() == nextDirection:
        mouse.turnRight()
    elif currentDirection != nextDirection:
        mouse.turnAround()
    mouse.moveForward()

def getNextCell(maze, mouse):
    initial = mouse.getPosition()
    center = None
    ancestors = {}
    queue = collections.deque([initial])
    while queue:
        current = queue.popleft()
        for direction in Direction:
            neighbor = getNeighbor(current, direction)
            # If the neighbor is out of bounds, skip
            if not maze.contains(neighbor):
                continue
            # If the neighbor is blocked by wall, skip
            if maze.getWall(current, direction):
                continue
            # If the neighbor is already discovered, skip
            if neighbor in ancestors:
                continue
            # Add the neighbor to queue and update ancestors
            queue.append(neighbor)
            ancestors[neighbor] = current
            if maze.inCenter(neighbor):
                center = neighbor
        # If a center cell was found, stop searching
        if center:
            break

    # Walk backwards from the center
    position = center
    while ancestors[position] != initial:
        position = ancestors[position]
    return position

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


def floodmaze(strt,fin):   # flood the maze from the strt cell to the fin cell
    global maze, walls, floodfail, debug, numcells
    floodstart = time.ticks_ms() # get time now
    floodclear()           # clear the flood table to all 283
    floodcleared = time.ticks_ms() # get time now
    floodcleared = floodcleared - floodstart
    flooded = 0            # set flag to not finished flooding yet
    floodfail = 0          # flag to show if flood failed to complete to end point
    curr = strt            # current cell being processed
    floodval = 0
    maze[strt] = 1         # set start cell flood value to one
    n = 0   # index for processing list array of cells to say where to add to end of list
    nxt = 0                # pointer to the first unprocessed item on the list
    while (flooded == 0):
        fval = maze[curr]  # get current value of current cell
        if ((walls[curr] & SOUTH) == 0):     # is there a gap to the SOUTH of current cell
            if (maze[curr - TABLEWIDTH] == numcells):
                maze[curr - TABLEWIDTH] = fval + 1    # set flood value in this cell
                proclist[n] = curr-TABLEWIDTH    # save flood cell for future processing
                n = n + 1                        # update processing list number
                if (proclist[n-1] == fin):       # check if finished flooding
                    flooded = 1                  # set flag to stop loop
        if ((walls[curr] & EAST) == 0):      # is there a gap to the EAST of current cell
            if (maze[curr + 1] == numcells):
                maze[curr + 1] = fval + 1        # set flood value in this cell
                proclist[n] = curr + 1           # save flood cell for future processing
                n = n + 1                        # update processing list number
                if (proclist[n-1] == fin):           # check if finished flooding
                    flooded = 1                      # set flag to stop loop
        if ((walls[curr] & NORTH) == 0):     # is there a gap to the NORTH of current cell
            if (maze[curr + TABLEWIDTH] == numcells):
                maze[curr + TABLEWIDTH] = fval + 1    # set flood value in this cell
                proclist[n] = curr + TABLEWIDTH  # save flood cell for future processing
                n = n + 1                        # update processing list number
                if (proclist[n-1] == fin):           # check if finished flooding
                       flooded = 1                      # set flag to stop loop
        if ((walls[curr] & WEST) == 0):      # is there a gap to the WEST of current cell
            if (maze[curr - 1] == numcells):
                maze[curr - 1] = fval + 1        # set flood value in this cell
                proclist[n] = curr - 1           # save flood cell for future processing
                n = n + 1                        # update processing list number
                if (proclist[n-1] == fin):       # check if finished flooding
                    flooded = 1                  # set flag to stop loop
        #print (proclist[n-1] , fin)
         # print (strt, fin, nxt, n, proclist)
        
        curr = proclist[nxt]             # get the location of the next cell to process
        nxt = nxt + 1                        # point to next item to process on the list
        
        if (nxt > n):    # check if flood unable to continue as no more cells accessible
            floodfail = 1                     # set flood failure status flag
            flooded = 1 # stop  the flooding loop
            if (debug == 1):
                print (strt, fin, nxt, n, proclist)
        #print ("after flood")
        #showflood()
    floodend = time.ticks_ms() # get time now
    floodtime = floodend - floodstart
    if (debug == 1):
        print ("floodtime", floodtime, " cleared", floodcleared )
    return                                    # return 
    
        #print (curr, n, nxt, fval, proclist[n-1])
  
    #showflood()
    #showwalls()
    #halt()    