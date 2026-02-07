# READ ME: Hey friends! This is my test bed for the maze solving algorithm. It works on a node-by-node basis, first imagining
# an N by N (9 by 9 by default) maze and virtually walking from node zero (top left), to the center node.

# Only library to install prior to running should be the pygame library, this is only used for visualisation
# and keypress inputs and won't be needed for the robot code

# Run this file without arguments to see my most recent 9 by 9 maze experiment, controls are as follows:

# SPACE: Advance the solver by a step, if the solver comes across a dead end it takes a step to designate
# that node as a dead end then reverse course to the parent node
# ESC: Quit the program
# C: A debugging input, shows the taxi-cab distance from the center to each given cell as a different hue
# P: Similar debugging output, taxi-cab distance from start to each cell as a different hue


# try:
import kris_robot
# except:
#     pass


dummy_plug = True


def rotate_walls():
    """
    A useful function for modifying wall codes to account for the physical orientation of the robot during motion
    """
    pass

UP = 0b0001
RIGHT = 0b0010
DOWN = 0b0100
LEFT = 0b1000


class NODE:
    """
    Individual grid cells in the mazes to be solved
    """
    # def __init__(self, pos, rank, code = 0):
    def __init__(self, pos: int, maze_size: int, code = 0):
        self.pos = pos
        self.x = pos % maze_size
        self.y = int(pos/maze_size)
        # self.rank = rank
        self.code = code
        # self.edge = ""
        self.fixed_dist_end = abs(self.x-int(maze_size/2)) + abs(self.y-int(maze_size/2))
        self.fixed_dist_start = self.x + self.y
        self.dist_end = self.fixed_dist_end
        self.dist_start = self.fixed_dist_start
        self.parent = -1
        self.flood_parent = -1
        self.children = []
        self.dead_end = False
        self.updated = False
        self.delay = 0
        self.gate = 0
        self.explored = False

        pass


class MAZESOLVER:
    """
    Uses A* style path planning to determine the shortest route to a location, currently under construction, will be usurped by
    a larger navigator class later
    """
    def create_maze(self): #placeholder
        pass

    def __init__(self, maze_size: int):
        try:
            if maze_size<1:
                IndexError
        except IndexError:
            print("IndexError, maze size must be greater than 0")
            exit
        
        
        # print("I am alive")
        self.current_node_pos = 0
        self.maze_size = maze_size
        self.start_point = 0
        self.end_point = int((self.maze_size**2)/2)
        self.path = [0]
        self.nodes = self.create_maze()
        self.solved = False
        
        self.direction = 1      # To begin with, assuming pointing to the right with respect to a fixed maze with origin in the top left corner

        # self.path.append(node(0)) 

    def create_maze(self):    # Creates an N^2 long list of NODE instances, organized into an N*N grid for the purposes of maze
                                        # tracking and solving
        nodes = []
        for i in range(self.maze_size**2):

            nodes.append(NODE(pos = i,maze_size=self.maze_size)) #generates a NODE instance and stores it in the list "nodes"
                                        # to be passed to the maze solving algorithm
            node = nodes[i]
            if node.x == 0:
                node.code |= LEFT
            elif node.x == self.maze_size-1:
                node.code |= RIGHT
            if node.y == 0:
                node.code |= UP
            elif node.y == self.maze_size-1:
                node.code |= DOWN
                
        return nodes

    def update_adjacent_walls(self, current_node: NODE):
        if current_node.code & UP and current_node.y > 0:
            self.nodes[self.xy_to_pos(current_node.x,current_node.y-1)].code |= DOWN
        if current_node.code & RIGHT and current_node.x < self.maze_size-1:
            self.nodes[self.xy_to_pos(current_node.x+1,current_node.y)].code |= LEFT
        if current_node.code & DOWN and current_node.y < self.maze_size-1:
            self.nodes[self.xy_to_pos(current_node.x,current_node.y+1)].code |= UP
        if current_node.code & LEFT and current_node.x > 0:
            self.nodes[self.xy_to_pos(current_node.x-1,current_node.y)].code |= RIGHT
        return

    def xy_to_pos(self, x: int,y: int):
        return x + self.maze_size*y

    def pos_to_xy(self, pos: int):
        return int(pos % self.maze_size), int(pos/self.maze_size)

    def get_node_children(self, current_node: NODE, flood_fill: bool = False):
        code = current_node.code
        children = []
        if not (code & RIGHT):    
            children.append(current_node.pos+1)
        if not (code & DOWN):
            children.append(current_node.pos+self.maze_size)
        if not (code & LEFT):
            children.append(current_node.pos-1)
        if not (code & UP):
            children.append(current_node.pos-self.maze_size)
        
        for child in children:
            if (child == current_node.parent and not flood_fill):
                children.remove(child)
                return children
        
        looping = True
        while flood_fill and looping:
            if any([self.nodes[child].updated for child in children]):
                for child in children:
                    if self.nodes[child].updated:
                        children.remove(child)
            else:
                looping = False
        if flood_fill:
            for child in children:
                if self.nodes[child].flood_parent == -1:
                    self.nodes[child].flood_parent = current_node.pos
        return children


    def next_child(self, current_node: NODE):
        
        current_choice = -1

        for child in current_node.children:
            if self.nodes[child].dead_end == True or any([child == path_step for path_step in self.path]):
                continue
            elif current_choice < 0:
                current_choice = child
            elif self.nodes[child].dist_end < self.nodes[current_choice].dist_end:
                current_choice = child
        
        return current_choice

    def flood_update(self, end_node_pos: NODE, green_gate: bool = False):
        new_children = [end_node_pos]
        end_node = self.nodes[end_node_pos]
        end_node.dist_end = 0
        while any (node.updated == False for node in self.nodes):
            children = new_children
            new_children = []
            i = 0
            while i < len(children):
                node_pos = children[i]
                node = self.nodes[node_pos]
                node.dist_end = self.nodes[node.flood_parent].dist_end + 1 if (node != end_node and not node.updated) else node.dist_end #each node receives the distance from its parent in the flood fill
                if not node.updated and node.gate:
                    if node.gate == -1:
                        node.delay = 3
                    elif node.gate == 1:
                        parent_node = node_pos
                        while parent_node != end_node.pos:
                            self.nodes[parent_node].dist_end -= 1
                            parent_node = self.nodes[parent_node].flood_parent
                            # print("yeah we got stuck here")
                        for reset_node in self.nodes:
                            reset_node.dist_end += 1
                        end_node.dist_end = 0
                        children.extend(self.get_node_children(node, flood_fill=True))

                node.updated = True

                if node.delay > 0:
                    new_children.append(node_pos)
                    children.remove(node.pos)
                    i -= 1
                    node.delay -= 1
                    node.dist_end += 1
                elif node.gate < 1:
                    new_children.extend(self.get_node_children(node, flood_fill=True))
                i += 1

            new_children = list(set(new_children)-set(children))
            new_children.sort()                       

        for node in self.nodes:
            node.updated = False
            node.delay = 0
            node.flood_parent = -1
        return



    def step(self, flood_fill: bool = False):
        
        if self.current_node_pos == self.end_point:
            # self.solved = True
            # self.flood_update(self.nodes[self.end_point]) #checking how the walls around the end affect the rest of the map
            return  self.pos_to_xy(self.current_node_pos)
        
        
        current_node = self.nodes[self.current_node_pos]

        if flood_fill:
            self.flood_update(self.end_point)


        # if current_node.dead_end == True:
        #     self.path.pop()
        #     self.current_node_pos = current_node.parent

        current_node.children.clear()
        current_node.children = self.get_node_children(current_node)

        # print("There are " + str(len(current_node.children)) + " children on this node")
        # print("and the positions of the children are")
        # for i in range(len(current_node.children)):
        #     print(str(current_node.children[i]))
        
        if len(current_node.children) < 1 or all([self.nodes[child].dead_end == True for child in current_node.children]):
            next_child = -1
        elif len(current_node.children) == 1 and not any([current_node.children[0] == path_step for path_step in self.path]):
            next_child = current_node.children[0]
        else:
            next_child = self.next_child(current_node)
            pass
        # print("wow i can't believe that worked")

        if next_child == -1:
            current_node.dead_end = True
            # print("dead end reached")
            self.path.pop()
            self.current_node_pos = current_node.parent
        else:
            self.nodes[next_child].parent = self.current_node_pos
            self.path.append(next_child)
            self.current_node_pos = next_child
        
        return self.nodes[self.current_node_pos].x, self.nodes[self.current_node_pos].y

    #END OF MAZESOLVER CLASS

    
class ROBOT_CONTROL:
    """
    Dummy plug while programming the logic and pathfinding
    """
    def __init__(self, maze_size, inverted: bool = False):
        self.x = 0
        self.y = 0
        self.maze_size = maze_size
        self.direction = 2
        self.inverted = inverted
        self.pos = 0


# Here's where it gets complicated, each cell (node) has a 4 bit code corresponding to the configuration of the walls, the least significant bit
# represents a wall to the top, increasing bit significance proceeds clockwise around the centre of the node from there. A single wall to the right
# would be given by 0010, a wall above and below is 0101, and three walls except for the one below would be 1011. The decimal representation of these
# 4 bit codes are how I store the wall configurations, as you'll see below


        self.fixed_codes = [9, 5, 5, 1, 1, 5, 5, 1, 3, 10, 13, 1, 0, 4, 5, 3, 10, 10, 8, 3, 8, 2, 9, 5, 6, 8, 2, 14, 10, 12, 6, 12, 5, 3, 10, 10, 11, 8, 7, 11, 11, 9, 6, 8, 2, 8, 2, 9, 2, 10, 12, 3, 10, 10, 10, 10, 12, 2, 10, 9, 6, 8, 2, 10, 12, 3, 10, 10, 12, 5, 2, 10, 12, 7, 12, 4, 4, 5, 5, 4, 6]
        self.red_gates = [41, 18, 19]
        self.green_gates = [58, 2]
        if self.inverted:
            inverted_codes = [rotate_walls(code,2) for code in (fixed_codes)]
            inverted_codes.reverse()
            fixed_codes = inverted_codes

        return


# if "kris_robot" in dir() and not dummy_plug:
    def get_walls(self):
        sensor_walls = kris_robot.get_walls()
        code = rotate_walls(sensor_walls, self.direction)
        return code
# else:
    # def get_walls(self):

    #     return self.fixed_codes[self.pos]

# if "kris_robot" in dir() and not dummy_plug:
    # def get_gate(self):
    #     return kris_robot.get_gate()
# else:
    def get_gate(self):
        
        try:
            self.red_gates.index(self.pos)
            return -1
        except:
            pass
        try:
            self.green_gates.index(self.pos)
            return 1
        except:
            pass
        
        return 0

# if "kris_robot" in dir():
    def rotate(self, new_dir, code):
        #add motor control here
        diff = new_dir - self.direction
        if abs(diff) > 2:
            diff *= -1/3
            kris_robot.rotate(diff)
        elif abs(diff)==2:
            if rotate_walls(code,-self.direction) & LEFT:
                kris_robot.rotate(1)
                kris_robot.bonk()
                kris_robot.rotate(1)
            elif rotate_walls(code,-self.direction) & RIGHT:
                kris_robot.rotate(-1)
                kris_robot.bonk()
                kris_robot.rotate(-1)
        else:
            kris_robot.rotate(diff)
        self.direction = int((self.direction + diff) % 4)
        return self.direction
# else:
    # def rotate(self, new_dir, code):
    #     diff = new_dir - self.direction
    #     if abs(diff) > 2:
    #         diff *= -1/3
    #     self.direction = int((self.direction + diff) % 4)
    #     return self.direction

# if "kris_robot" in dir():
    def forward(self):
        kris_robot.forward()
        if self.direction % 2:
            self.x = self.x - self.direction + 2
        else:
            self.y = self.y + self.direction - 1
# else:
    # def forward(self):
    #     if self.direction % 2:
    #         self.x = self.x - self.direction + 2
    #     else:
    #         self.y = self.y + self.direction - 1

# if "kris_robot" in dir():
    def bonk(self):
        kris_robot.bonk()
        print("bonk")
# else:
    # def bonk(self):
    #     print("bonk")
    
    


    #END OF ROBOT_CONTROL CLASS


class NAVIGATOR:

    def __init__(self, maze_size: int):
        
        self.maze_size = maze_size
        self.orienting = True   #The initial state of the solver, feeling its way through the first corridor and determining if it is facing
                                # to the right or down with respect to a maze with origin in the top left corner
        self.solved = False
        self.solver = MAZESOLVER(maze_size=maze_size)
        self.start_point = 0
        self.end_point = int((self.maze_size**2)/2)

        
        self.robot = ROBOT_CONTROL(maze_size=maze_size)
        self.robot.direction = self.solver.direction

    def move_goto(self, x, y):
        robot = self.robot
        #add motor control here
        code = self.solver.nodes[robot.pos].code
        if robot.x == x and robot.y == y:
            return -1
        elif robot.x < x:
            robot.rotate(1, code)
        elif robot.x > x:
            robot.rotate(3, code)
        elif robot.y < y:
            robot.rotate(2, code)
        elif robot.y > y:
            robot.rotate(0, code)
        
        if (1<<robot.direction) & rotate_walls(code,2):
            robot.bonk()

        robot.forward()
        robot.pos = robot.y * self.maze_size + robot.x
        print(robot.pos)
        return

    def forward_solve(self, complete_solve: bool = False):
        solver = self.solver
        robot = self.robot
        solver.solved = False
        solver.flood_update(self.end_point)
        solver.current_node_pos = robot.pos

        solver.path.clear()
        for node in range(self.maze_size**2):        #To clear dependencies for reverse solving
            solver.nodes[node].parent = -1
        solver.path.append(solver.current_node_pos)
        solver.start_point = solver.current_node_pos
        solver.end_point = self.end_point
        solver.nodes[solver.current_node_pos].code |= robot.get_walls()
        solver.nodes[solver.current_node_pos].gate = robot.get_gate()
        solver.update_adjacent_walls(solver.nodes[solver.current_node_pos])
        solver.nodes[solver.current_node_pos].explored = True
        x, y = solver.step()

        while True:

            if (solver.xy_to_pos(x,y) == solver.end_point):
                if not complete_solve:
                    break
                else:
                    self.move_goto(x,y)
                    solver.direction = robot.direction
                    solver.current_node_pos = robot.pos
                    break
            self.move_goto(x,y)
            solver.direction = robot.direction
            solver.current_node_pos = robot.pos
            solver.nodes[solver.current_node_pos].code |= robot.get_walls()
            solver.nodes[solver.current_node_pos].gate = robot.get_gate()
            solver.update_adjacent_walls(solver.nodes[solver.current_node_pos])
            solver.nodes[solver.current_node_pos].explored = True
            x, y = solver.step()
            self.solved = solver.solved
        return solver.path

    def reverse_solve(self):
        solver = self.solver
        robot = self.robot
        solver.flood_update(self.start_point)

        solver.path.clear()
        for node in range(self.maze_size**2):        #To clear dependencies for reverse solving
            solver.nodes[node].parent = -1 
        solver.start_point = robot.pos
        solver.current_node_pos = robot.pos
        solver.nodes[self.end_point].dead_end = True    #makes sure the robot doesn't wander through
                                                        #the end point for the hell of it
        solver.end_point = self.start_point
        solver.path.append(solver.current_node_pos)
        solver.nodes[solver.current_node_pos].code |= robot.get_walls()
        solver.nodes[solver.current_node_pos].gate = robot.get_gate()
        solver.update_adjacent_walls(solver.nodes[solver.current_node_pos])
        solver.nodes[solver.current_node_pos].explored = True

        while solver.current_node_pos != solver.end_point:
            
            x, y = solver.step()
            self.move_goto(x,y)
            solver.direction = robot.direction
            solver.current_node_pos = robot.pos
            solver.nodes[solver.current_node_pos].code |= robot.get_walls()
            solver.nodes[solver.current_node_pos].gate = robot.get_gate()
            solver.update_adjacent_walls(solver.nodes[solver.current_node_pos])
            
            solver.nodes[solver.current_node_pos].explored = True
            self.solved = solver.solved
        solver.nodes[self.end_point].dead_end = False
        return solver.path
    
    def theoretical_forward_solve(self):
        solver = self.solver
        solver.flood_update(self.end_point)

        solver.path.clear()
        for node in range(self.maze_size**2):        #To clear dependencies for reverse solving
            solver.nodes[node].parent = -1

        solver.path.append(0)
        solver.current_node_pos = 0
        solver.start_point = self.start_point
        solver.end_point = self.end_point
        x, y = solver.step()

        while True:
            if (solver.xy_to_pos(x,y) == solver.end_point):
                break
            x, y = solver.step()
        return solver.path


    def complete_solve(self):
        while not self.solved:
            self.forward_solve()
            self.reverse_solve()
            path = self.theoretical_forward_solve()
            if all(self.solver.nodes[node].explored for node in path[:-1]):
                new_path = self.forward_solve(complete_solve=True)
                print("Robot currently at " + str(self.robot.pos))
                self.solved = True
        if new_path == path:
            print("seems all good")
            print(new_path)
            self.reverse_solve()
            print("Robot is at " + str(self.robot.pos))
            path = self.theoretical_forward_solve()
            for pos in path:
                x,y = self.solver.pos_to_xy(pos)
                self.move_goto(x,y)
            print("Robot is now at " + str(self.robot.pos))
        else:
            print("we have a new problem")
            print(path)
            print(new_path)
        
        return
    
    # Deprecated
    # def step(self):
    #     solver = self.solver
    #     robot = self.robot
        
    #     walls = rotate_walls(robot.get_walls(),robot.direction)
    #     solver.nodes[solver.current_node_pos].code = walls
    #     solver.nodes[solver.current_node_pos].gate = robot.get_gate()
    #     solver.update_adjacent_walls(solver.nodes[solver.current_node_pos])
    #     x, y = solver.step()
    #     solver.nodes[solver.current_node_pos].explored = True
    #     self.move_goto(x,y)
    #     self.solved = solver.solved
    #     return
    pass



# Below is a small function for rotating the detected wall configuration to compensate for the direction the robot will be facing during operation

# A useful function for modifying wall codes to account for the physical orientation of the robot during motion
def rotate_walls(code,current_direction):
    """
    A useful function for modifying wall codes to account for the physical orientation of the robot during motion
    """
    temp_code = code << (current_direction % 4)

    return int(temp_code / 16) + (temp_code % 16)


if __name__ == "__main__":

    import pygame
    import colorsys
    import sys

    def draw_walls(screen: pygame.Surface,rect_start_x: int, rect_start_y: int, square_size: int, code: int):
        top_left = (rect_start_x - 1, rect_start_y - 1)
        top_right = (rect_start_x + square_size, rect_start_y - 1)
        bottom_left = (rect_start_x - 1, rect_start_y + square_size)
        bottom_right = (rect_start_x + square_size, rect_start_y + square_size)
        if code & RIGHT:
            pygame.draw.line(screen, "black", top_right, bottom_right,5)
        if code & DOWN:
            pygame.draw.line(screen, "black", bottom_left, bottom_right,5)
        if code & LEFT:
            pygame.draw.line(screen, "black", top_left, bottom_left,5)
        if code & UP:
            pygame.draw.line(screen, "black", top_left, top_right,5)
        return

    pygame.init()
    screen = pygame.display.set_mode((640, 720))
    # map = pygame.display.set_mode((640,720))
    clock = pygame.time.Clock()

    maze_size = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    fixed_maze = bool(sys.argv[2]) if len(sys.argv) > 2 else True
    square_size = int((screen.get_width()-10)/maze_size)-1
    maze_centre = (int(maze_size/2),int(maze_size/2))
    display_colors = False
    display_distance = False
    display_ranks = False
    inverted = False # Set this to true to turn whatever maze you input upside down

    value = 1
    saturation = 0.5

    navigator = NAVIGATOR(9)

    running = True
    

    forward = True
    
    # navigator.solver.flood_update(navigator.end_point)
    # navigator.theoretical_forward_solve()
    # # navigator.reverse_solve()
    while running:
        # if navigator.solved:
        #     running = False
        # else:
        #     navigator.step()

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_r:
                    pass
                #     nodes = create_maze(maze_size)
                elif key == pygame.K_ESCAPE:
                    running = False
                elif key == pygame.K_SPACE:
                    if navigator.solved:
                        # running = False
                        pass
                    else:
                        # if forward:
                        #     navigator.forward_solve()
                        #     navigator.theoretical_forward_solve()
                        #     forward = False
                        #     print(navigator.robot.pos)
                        # else:
                        #     navigator.reverse_solve()
                        #     navigator.theoretical_forward_solve()
                        #     forward = True
                        #     print(navigator.robot.pos)
                        navigator.complete_solve()
                elif key == pygame.K_c:
                    display_distance = False
                    display_ranks = False
                    display_colors = True if display_colors == False else False
                elif key == pygame.K_p:
                    display_colors = False
                    display_ranks = False
                    display_distance = True if display_distance == False else False
                elif key == pygame.K_l:
                    display_colors = False
                    display_distance = False
                    display_ranks = True if display_distance == False else False
                else:
                    print("Well here we are again")

            
        
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("navy")
        # map.fill("navy")
        for node in navigator.solver.nodes:
            x = 5 + (node.x) * (square_size + 1)
            y = 45 + int(node.y) * (square_size + 1)
            
            if display_colors:
                rgb = tuple(round(j*255) for j in  colorsys.hsv_to_rgb(node.dist_end/maze_size,saturation,value))
            elif display_distance:
                rgb = tuple(round(j*255) for j in  colorsys.hsv_to_rgb(node.dist_start/maze_size,saturation,value))
            # elif display_ranks:
            #     rgb = tuple(round(i*255) for i in  colorsys.hsv_to_rgb(solver.nodes[i].rank/maze_size**2,saturation,value))
            else:            
                if any(node.pos == path_step for path_step in navigator.solver.path):
                    if navigator.solver.solved == True:
                        rgb = (0,255,0)
                    elif node.gate == -1:
                        rgb = (255,0,0)
                    elif node.gate == 1:
                        rgb = (0,255,0)
                    else:
                        rgb = (0,0,255)
                elif node.dead_end == True:
                    rgb = (100,100,30)
                elif node.explored:
                    rgb = (100,100,100)
                else:
                    rgb = (255,255,255)
            pygame.draw.rect(screen, rgb, (x,y,square_size,square_size))
            # pygame.draw.rect(map, rgb, (x,y,square_size,square_size))
        # for i in range(maze_size**2):
        #     x = 5 + (i % maze_size) * (square_size + 1)
        #     y = 45 + int(i/maze_size) * (square_size + 1)
            draw_walls(screen,x,y,square_size, node.code)
            # draw_walls(map,x,y,fixed_codes[node.pos])


        # screen.fill("white")

        # RENDER YOUR GAME HERE

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()
