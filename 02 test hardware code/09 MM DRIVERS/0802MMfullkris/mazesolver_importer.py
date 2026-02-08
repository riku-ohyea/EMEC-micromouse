# import pygame
# import Prototype_solver
# import sys
# import colorsys


# UP = 0b0001
# RIGHT = 0b0010
# DOWN = 0b0100
# LEFT = 0b1000

# pygame.init()
# screen = pygame.display.set_mode((640, 720))
# # map = pygame.display.set_mode((640,720))
# clock = pygame.time.Clock()

# maze_size = int(sys.argv[1]) if len(sys.argv) > 1 else 9
# fixed_maze = bool(sys.argv[2]) if len(sys.argv) > 2 else True
# square_size = int((screen.get_width()-10)/maze_size)-1
# maze_centre = (int(maze_size/2),int(maze_size/2))
# display_colors = False
# display_distance = False
# display_ranks = False
# inverted = False # Set this to true to turn whatever maze you input upside down

# value = 1
# saturation = 0.5

# solver = Prototype_solver.MAZESOLVER(maze_size=maze_size)
# robot = Prototype_solver.ROBOT_CONTROL(maze_size=maze_size, inverted = inverted)
# robot.direction = solver.direction
# running = True

# def draw_walls(screen: pygame.Surface,rect_start_x: int, rect_start_y: int, square_size: int, code: int):
#     top_left = (rect_start_x - 1, rect_start_y - 1)
#     top_right = (rect_start_x + square_size, rect_start_y - 1)
#     bottom_left = (rect_start_x - 1, rect_start_y + square_size)
#     bottom_right = (rect_start_x + square_size, rect_start_y + square_size)
#     if code & RIGHT:
#         pygame.draw.line(screen, "black", top_right, bottom_right,5)
#     if code & DOWN:
#         pygame.draw.line(screen, "black", bottom_left, bottom_right,5)
#     if code & LEFT:
#         pygame.draw.line(screen, "black", top_left, bottom_left,5)
#     if code & UP:
#         pygame.draw.line(screen, "black", top_left, top_right,5)
#     return


# while running:
    

#     # poll for events
#     # pygame.QUIT event means the user clicked X to close your window
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#         if event.type == pygame.KEYDOWN:
#             key = event.key
#             if key == pygame.K_r:
#                 pass
#             #     nodes = create_maze(maze_size)
#             elif key == pygame.K_ESCAPE:
#                 running = False
#             elif key == pygame.K_SPACE:
#                 if solver.solved:
#                     running = False
#                 else:
#                     Prototype_solver.step(solver,robot)
#             elif key == pygame.K_c:
#                 display_distance = False
#                 display_ranks = False
#                 display_colors = True if display_colors == False else False
#             elif key == pygame.K_p:
#                 display_colors = False
#                 display_ranks = False
#                 display_distance = True if display_distance == False else False
#             elif key == pygame.K_l:
#                 display_colors = False
#                 display_distance = False
#                 display_ranks = True if display_distance == False else False
#             else:
#                 print("Well here we are again")

        
    
#     # fill the screen with a color to wipe away anything from last frame
#     screen.fill("navy")
#     # map.fill("navy")
#     for node in solver.nodes:
#         x = 5 + (node.x) * (square_size + 1)
#         y = 45 + int(node.y) * (square_size + 1)
        
#         if display_colors:
#             rgb = tuple(round(j*255) for j in  colorsys.hsv_to_rgb(node.dist_end/maze_size,saturation,value))
#         elif display_distance:
#             rgb = tuple(round(j*255) for j in  colorsys.hsv_to_rgb(node.dist_start/maze_size,saturation,value))
#         # elif display_ranks:
#         #     rgb = tuple(round(i*255) for i in  colorsys.hsv_to_rgb(solver.nodes[i].rank/maze_size**2,saturation,value))
#         else:            
#             if any(node.pos == path_step for path_step in solver.path):
#                     if solver.solved == True:
#                         rgb = (0,255,0)
#                     elif node.gate == -1:
#                         rgb = (255,0,0)
#                     elif node.gate == 1:
#                         rgb = (0,255,0)
#                     else:
#                         rgb = (0,0,255)
#             elif node.dead_end == True:
#                 rgb = (100,100,30)
#             else:
#                 rgb = (255,255,255)
#         pygame.draw.rect(screen, rgb, (x,y,square_size,square_size))
#         # pygame.draw.rect(map, rgb, (x,y,square_size,square_size))
#     # for i in range(maze_size**2):
#     #     x = 5 + (i % maze_size) * (square_size + 1)
#     #     y = 45 + int(i/maze_size) * (square_size + 1)
#         draw_walls(screen,x,y, square_size, node.code)
#         # draw_walls(map,x,y,fixed_codes[node.pos])


#     # screen.fill("white")

#     # RENDER YOUR GAME HERE

#     # flip() the display to put your work on screen
#     pygame.display.flip()

#     clock.tick(60)  # limits FPS to 60

# pygame.quit()

import Prototype_solver
import time


maze_size = 9

navigator = Prototype_solver.NAVIGATOR(9)

tic = time.time_ns()
navigator.complete_solve()
print(navigator.robot.pos)
toc = time.time_ns()
print(toc-tic)