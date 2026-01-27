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



import pygame
import sys
from random import randint
import colorsys

pygame.init()
screen = pygame.display.set_mode((640, 720))
clock = pygame.time.Clock()
running = True
display_colors = False
display_distance = False
display_ranks = False
inverted = False # Set this to true to turn whatever maze you input upside down


maze_size = int(sys.argv[1]) if len(sys.argv) > 1 else 9
fixed_maze = bool(sys.argv[2]) if len(sys.argv) > 2 else True
square_size = int((screen.get_width()-10)/maze_size)-1
maze_centre = (int(maze_size/2),int(maze_size/2))

middle = pygame.Vector2(screen.get_width()/2, screen.get_height()/2)

value = 1
saturation = 0.5

# Below is a small function for rotating the detected wall configuration to compensate for the direction the robot will be facing during operation

def rotate_walls(code,current_direction):

        temp_code = code * current_direction

        return int(temp_code / 16) + (temp_code % 16)


# Here's where it gets complicated, each cell (node) has a 4 bit code corresponding to the configuration of the walls, the least significant bit
# represents a wall to the right, increasing bit significance proceeds clockwise around the centre of the node from there. A single wall to the right
# would be given by 0001, a wall above and below is 1010, and three walls except for the one below would be 1101. The decimal representation of these
# 4 bit codes are how I store the wall configurations, as you'll see below

fixed_codes = [12, 11, 12, 11, 13, 5, 14, 2, 8, 3, 4, 9, 14, 0, 9, 5, 4, 10, 3, 7, 7, 6, 10, 10, 11]
fixed_codes = [12, 10, 8, 9, 13, 5, 12, 3, 6, 1, 5, 5, 14, 9, 5, 5, 5, 13, 5, 5, 6, 3, 6, 2, 3]
fixed_codes = [12,10,10,8,8,10,10,8,9,5,14,8,0,2,10,9,5,5,4,9,4,1,12,10,3,4,1,7,5,6,3,6,10,9,5,5,13,4,11,13,13,12,3,4,1,4,1,12,1,5,6,9,5,5,5,5,6,1,5,12,3,4,1,5,6,9,5,5,6,10,1,5,6,11,6,2,2,10,10,2,3]

inverted_codes = [rotate_walls(code,4) for code in (fixed_codes)]
inverted_codes.reverse()


class NODE:

    # def __init__(self, pos, rank, code = 0):
    def __init__(self, pos, code = 0):
        self.pos = pos
        self.x = pos % maze_size
        self.y = int(pos/maze_size)
        # self.rank = rank
        self.code = code
        # self.edge = ""
        self.fixed_dist_end = abs(self.x-maze_centre[0]) + abs(self.y-maze_centre[1])
        self.fixed_dist_start = self.x + self.y
        self.dist_end = self.fixed_dist_end
        self.dist_start = self.fixed_dist_start
        self.parent = -1
        self.children = []
        self.dead_end = False

        pass


class MAZESOLVER:
    
    def create_maze(self): #placeholder
        pass

    def __init__(self, maze_size: int):
        
        try:
            if maze_size<1:
                IndexError
        except IndexError:
            print("IndexError, maze size must be greater than 0")
            exit
        
        
        print("I am alive")
        self.start_point = 0
        self.current_node_pos = 0
        self.maze_size = maze_size
        self.end_point = int((self.maze_size**2)/2)
        self.path = [0]
        self.nodes = self.create_maze()
        self.solved = False
        self.orienting = True   #The initial state of the solver, feeling its way through the first corridor and determining if it is facing
                                # to the right or down with respect to a maze with origin in the top left corner
        self.direction = 2      # To begin with, assuming pointing to the right with respect to a fixed maze with origin in the top left corner

        # self.path.append(node(0)) 

    def create_maze(self):    # Creates an N^2 long list of NODE instances, organized into an N*N grid for the purposes of maze
                                        # tracking and solving
        
        
        # ranks = []
        nodes = []

        # for i in range(maze_size**2):
        #     ranks.append(i)

        for i in range(self.maze_size**2):
            # rankpos = randint(0,len(ranks)-1) #creates a list of ranks that the nodes will
            # be randomly assigned to prevent conflicts of walls later
            # nodes.append(NODE(pos = i, rank = ranks[rankpos],code = randint(0,15))) #generate
            #a series of nodes, each of which corresponds to a cell of the maze, assign that node
            #a random configuration of walls, and a random rank from the remaining available ranks

            nodes.append(NODE(pos = i)) #generates a NODE instance and stores it in the list "nodes"
                                        # to be passed to the maze solving algorithm

            # ranks.pop(rankpos) #remove used ranks to prevent conflicts

            #The following set of if statements adds borders to the outer edge of the maze
            if nodes[i].x == 0:  #Left hand edge of maze
                nodes[i].code |= 4 
                # nodes[i].edge = "L"
            if nodes[i].x == self.maze_size - 1: #Right hand edge of maze
                nodes[i].code |= 1
                # nodes[i].edge = "R"
            if nodes[i].y == 0: #Top row of maze
                nodes[i].code |= 8
                # nodes[i].edge += "T"
            if nodes[i].y == self.maze_size - 1: #Bottom row of maze
                nodes[i].code |= 2
                # nodes[i].edge += "B"
            else: #Internal squares
                # nodes[i].edge = "I" 
                pass

            if fixed_maze == True:
                nodes[i].code = fixed_codes[i] if inverted == False else inverted_codes[i]
            
            #The following section is intended to use the ranks of the nodes to remove walls
            #that conflict with open sections or add walls so that neighbouring cells all agree
            #on the existence of a given wall

        # for node in nodes:
        #     #RHS Node
        #     if not node.edge[0] == "R":
        #         neighbour = nodes[node.pos + 1]
        #         if neighbour.rank > node.rank:
        #             pass
            

        return nodes

    def find_adjacents(self):
        return

    def get_node_children(self, current_node: NODE):
        code = current_node.code
        current_node.children.clear()
        if not (code & 1):    
            current_node.children.append(current_node.pos+1)
        if not (code & 2):
            current_node.children.append(current_node.pos+self.maze_size)
        if not (code & 4):
            current_node.children.append(current_node.pos-1)
        if not (code & 8):
            current_node.children.append(current_node.pos-self.maze_size)
        for i in range(len(current_node.children)):
            if current_node.children[i] == current_node.parent:
                current_node.children.pop(i)
                break
        return


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



    def step(self):
        if self.current_node_pos == self.end_point:
            self.solved = True
            return
        
        
        current_node = self.nodes[self.current_node_pos]

        if current_node.dead_end == True:
            self.path.pop()
            self.current_node_pos = current_node.parent


        self.get_node_children(current_node)

        print("There are " + str(len(current_node.children)) + " children on this node")
        print("and the positions of the children are")
        for i in range(len(current_node.children)):
            print(str(current_node.children[i]))
        
        if len(current_node.children) < 1 or all([self.nodes[child].dead_end == True for child in current_node.children]):
            current_node.dead_end = True
            print("dead end reached")
            next_child = -1
        elif len(current_node.children) == 1 and not any([current_node.children[0] == path_step for path_step in self.path]):
            next_child = current_node.children[0]
        else:
            next_child = self.next_child(current_node)
            pass
        
        print("wow i can't believe that worked")

        if next_child == -1:
            current_node.dead_end = True
            print("dead end reached")
        else:
            self.nodes[next_child].parent = self.current_node_pos
            self.path.append(next_child)
            self.current_node_pos = next_child
        
        return

        
        
            
        

        return



    



    

    



def draw_walls(screen: pygame.Surface,rect_start_x: int, rect_start_y: int, code: int):
    top_left = (rect_start_x - 1, rect_start_y - 1)
    top_right = (rect_start_x + square_size, rect_start_y - 1)
    bottom_left = (rect_start_x - 1, rect_start_y + square_size)
    bottom_right = (rect_start_x + square_size, rect_start_y + square_size)
    if code & 0b1 == 1:
        pygame.draw.line(screen, "black", top_right, bottom_right,5)
    if code & 0b10 == 0b10:
        pygame.draw.line(screen, "black", bottom_left, bottom_right,5)
    if code & 0b100 == 0b100:
        pygame.draw.line(screen, "black", top_left, bottom_left,5)
    if code & 0b1000 == 0b1000:
        pygame.draw.line(screen, "black", top_left, top_right,5)
    return




# nodes = create_maze(maze_size)  # Old code, create_maze() is now absorbed by the maze_solver class

solver = MAZESOLVER(maze_size=maze_size)

while running:
    

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
                if solver.solved:
                    running = False
                else:
                    solver.step()
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
    for node in solver.nodes:
        x = 5 + (node.x) * (square_size + 1)
        y = 45 + int(node.y) * (square_size + 1)
        
        if display_colors:
            rgb = tuple(round(j*255) for j in  colorsys.hsv_to_rgb(node.dist_end/maze_size,saturation,value))
        elif display_distance:
            rgb = tuple(round(j*255) for j in  colorsys.hsv_to_rgb(node.dist_start/maze_size,saturation,value))
        # elif display_ranks:
        #     rgb = tuple(round(i*255) for i in  colorsys.hsv_to_rgb(solver.nodes[i].rank/maze_size**2,saturation,value))
        else:            
            if any(node.pos == path_step for path_step in solver.path):
                if solver.solved == True:
                    rgb = (0,255,0)
                else:
                    rgb = (255,0,0)
            elif node.dead_end == True:
                rgb = (100,100,30)
            else:
                rgb = (255,255,255)
        pygame.draw.rect(screen, rgb, (x,y,square_size,square_size))
    # for i in range(maze_size**2):
    #     x = 5 + (i % maze_size) * (square_size + 1)
    #     y = 45 + int(i/maze_size) * (square_size + 1)
        draw_walls(screen,x,y,node.code)



    # screen.fill("white")

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()