import API
import collections

from Direction import Direction
from Maze import Maze
from Mouse import Mouse

import sys


def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()


INF = 10**9


def main():
    maze = Maze(API.mazeWidth(), API.mazeHeight())
    mouse = Mouse(0, 0, Direction.NORTH)

    width = API.mazeWidth()
    height = API.mazeHeight()

    # Initial cost grid (computed with currently-known walls: none yet)
    costs = computeFloodFillCosts(maze)

    drawCosts(costs, width, height)

    while not maze.inCenter(mouse.getPosition()):
        updateWalls(maze, mouse)

        # Recompute whenever we learn new walls (simple + robust)
        costs = computeFloodFillCosts(maze)

        drawCosts(costs, width, height)
        # optional: highlight current & accessible neighbors
        paintLocalDebug(maze, mouse, costs)
        # optional: detailed console debug
        logStep(maze, mouse, costs)

        moveOneCellFloodFill(maze, mouse, costs)


# def updateWalls(maze, mouse):
#     position = mouse.getPosition()
#     direction = mouse.getDirection()

#     # Front wall
#     if API.wallFront():
#         maze.setWall(position, direction)

#     # Left / Right walls (micropython compatible)
#     if API.wallLeft():
#         maze.setWall(position, Direction.turnLeft(direction))
#     if API.wallRight():
#         maze.setWall(position, Direction.turnRight(direction))

def updateWalls(maze, mouse):
    pos = mouse.getPosition()
    d = mouse.getDirection()

    if API.wallFront():
        setWallBothSides(maze, pos, d)

    if API.wallLeft():
        setWallBothSides(maze, pos, Direction.turnLeft(d))

    if API.wallRight():
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
        log("No accessible moves from current cell based on known walls.")
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
    API.clearAllText()  # clears previous numbers :contentReference[oaicite:2]{index=2}
    for x in range(width):
        for y in range(height):
            c = costs.get((x, y), INF)
            if c >= INF:
                # unreachable based on your KNOWN wall map
                API.setText(x, y, "##")
            else:
                API.setText(x, y, str(c))


def paintLocalDebug(maze, mouse, costs):
    """
    Colors current cell and accessible neighbors.
    """
    API.clearAllColor()  # optional, but makes it readable :contentReference[oaicite:3]{index=3}

    cur = mouse.getPosition()
    API.setColor(cur[0], cur[1], "y")  # current = yellow :contentReference[oaicite:4]{index=4}

    for d in Direction.ALL:
        nb = getNeighbor(cur, d)
        if not maze.contains(nb):
            continue
        if maze.getWall(cur, d):
            continue
        # accessible neighbor = green
        API.setColor(nb[0], nb[1], "g")  # :contentReference[oaicite:5]{index=5}


def logStep(maze, mouse, costs):
    """
    Prints current cost + each neighbor cost + whether blocked.
    This is the fastest way to find why you got stuck.
    """
    cur = mouse.getPosition()
    cur_dir = mouse.getDirection()
    log(f"@ {cur} heading={cur_dir} cost={costs.get(cur, INF)}")

    # show in tie-break order (forward > right > left > back)
    dirs = [
        ("F", cur_dir),
        ("R", Direction.turnRight(cur_dir)),
        ("L", Direction.turnLeft(cur_dir)),
        ("B", Direction.turnAround(cur_dir)),
    ]

    for label, d in dirs:
        nb = getNeighbor(cur, d)
        if not maze.contains(nb):
            log(f"  {label}: {nb} OOB")
            continue
        w = maze.getWall(cur, d)
        c = costs.get(nb, INF)
        log(f"  {label}: {nb} wall={w} cost={c}")

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
