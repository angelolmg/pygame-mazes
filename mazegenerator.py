import time
import pygame, sys
from random import randint, choice, seed
from math import sqrt
from pygame.locals import *

seed(1337)

def find_final_path():
    full_path = [target_node]
    tail_end = target_node

    while tail_end != start_node:
        tail_end = grid_matrix[tail_end[0]][tail_end[1]].last_index
        full_path.append(tail_end)
    
    reset_grid_matrix()

    # final animation
    initial = time.time()
    cool = 0.04
    i = len(full_path) - 1

    while(len(full_path) > 0):
        now = time.time()
        if now >= initial + cool:
            grid_matrix[full_path[i][0]][full_path[i][1]].path_node_state()
            draw_grid_matrix()
            pygame.display.update()
            del full_path[i]
            initial = now
            i -= 1
    
    print(time.time() - initial_time)

def available(index):
    x = index[0]
    y = index[1]

    if x < 0 or  x > (cell_count_col - 1) or y < 0 or y > (cell_count_row - 1):
            return False

    if not maze_done:
        if grid_matrix[x][y].being_carved == True:
            return False
    
    return True

def euclidian_distance_norm(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return int(10*(sqrt((x1-x2)**2 + (y1-y2)**2)))

def get_neighbours(index):
    x = index[0]
    y = index[1]

    current = grid_matrix[x][y]
    walls = current.walls

    # directions
    directions = []

    top = (x, y - 1)
    if available(top) and not walls[0]:
        node_top = grid_matrix[top[0]][top[1]]
        if not node_top.closed_path:
            directions.append(top)
        elif node_top.is_primary:
            directions.append(top)

    right = (x + 1, y)
    if available(right) and not walls[1]:
        node_right = grid_matrix[right[0]][right[1]]
        if not node_right.closed_path:
            directions.append(right)
        elif node_right.is_primary:
            directions.append(right)

    bottom = (x, y + 1)
    if available(bottom) and not walls[2]:
        node_bottom = grid_matrix[bottom[0]][bottom[1]]
        if not node_bottom.closed_path:
            directions.append(bottom)
        elif node_bottom.is_primary:
            directions.append(bottom)

    left = (x - 1, y)
    if available(left) and not walls[3]:
        node_left = grid_matrix[left[0]][left[1]]
        if not node_left.closed_path:
            directions.append(left)
        elif node_left.is_primary:
            directions.append(left)


    for direction in directions:
        grid_matrix[direction[0]][direction[1]].open_path_state()

        distance_from_start = euclidian_distance_norm(direction, start_node)
        distance_from_target = euclidian_distance_norm(direction, start_node)
        new_score = distance_from_start + distance_from_target

        if grid_matrix[direction[0]][direction[1]].star_score > new_score:
            grid_matrix[direction[0]][direction[1]].star_score = new_score
            grid_matrix[direction[0]][direction[1]].last_index = (x, y)
        
        global path_found
        if direction == target_node:
            path_found = True
            return target_node

    grid_matrix[x][y].closed_path_state()

    return directions

# A* pathfinding routine
def pathfind():
    min_score_node = max(open_list, key=lambda x: grid_matrix[x[0]][x[1]].star_score)
    open_list.remove(min_score_node)
    open_list.extend(get_neighbours(min_score_node))


class cell:
    def __init__(self, px, py, index):
        self.color = grey_color
        self.walls = [True, True, True, True]   #top, right, bottom and left
        self.rect = pygame.Rect(px, py, cell_side, cell_side)
        self.being_carved = False
        self.line_weight = 1
        self.index = index
        self.last_index = (0, 0)
        self.star_score = 999
        self.closed_path = False
        self.is_primary = False

    def draw(self):
        lw = self.line_weight
        pygame.draw.rect(screen, self.color, self.rect)

        if self.walls[0]:
            pygame.draw.rect(screen, black_color, (self.rect.left, self.rect.top, cell_side, lw))
        if self.walls[1]:
            pygame.draw.rect(screen, black_color, (self.rect.right - lw, self.rect.top, lw, cell_side))
        if self.walls[2]:
            pygame.draw.rect(screen, black_color, (self.rect.left, self.rect.bottom - lw, cell_side, lw))
        if self.walls[3]:
            pygame.draw.rect(screen, black_color, (self.rect.left, self.rect.top, lw, cell_side))

    # STATES
    def being_carved_state(self):
        self.being_carved = True
        self.color = red_color
        return self
    
    def reset_state(self):
        self.color = white_color

    def path_node_state(self):
        self.color = teal_color
        self.is_primary = True
        self.closed_path = True
        return self.index
    
    def open_path_state(self):
        if not self.is_primary:
            self.color = green_color
        return self.index
    
    def closed_path_state(self):
        if not self.is_primary:
            self.color = red_color
            self.closed_path = True
        return self.index
    
    def step(self):
        # build possible paths
        top = (self.index[0], self.index[1] - 1)
        right = (self.index[0] + 1, self.index[1])
        bottom = (self.index[0], self.index[1] + 1)
        left = (self.index[0] - 1, self.index[1])
        paths = [top, right, bottom, left]

        # remove unavailable paths
        available_paths = len(paths)
        for path_index in range(available_paths):
            if not available(paths[path_index]):
                paths[path_index] = None
                available_paths -= 1

        # choose random path from remaining (if theres any)
        if available_paths <= 0:
            return False
        else:
            global carve_path, grid_matrix
            next_index = None
            while (next_index == None):
                next_index = choice(paths)

            # removing separating wall between cells
            nx = next_index[0]
            ny = next_index[1]

            if next_index == top:
                self.walls[0] = False
                grid_matrix[nx][ny].walls[2] = False
            if next_index == right:
                self.walls[1] = False
                grid_matrix[nx][ny].walls[3] = False
            if next_index == bottom:
                self.walls[2] = False
                grid_matrix[nx][ny].walls[0] = False
            if next_index == left:
                self.walls[3] = False
                grid_matrix[nx][ny].walls[1] = False

            carve_path.append(grid_matrix[nx][ny])
            carve_path[-1].being_carved_state()

            return True

def reset_grid_matrix():
    for row in range(cell_count_row):
        for col in range(cell_count_col):
            grid_matrix[row][col].reset_state()

def draw_grid_matrix():
    for row in range(cell_count_row):
        for col in range(cell_count_col):
            grid_matrix[row][col].draw()

def init_cell_grid():
    global grid_matrix
    for row in range(cell_count_row):
        for col in range(cell_count_col):
            grid_matrix[row][col] = cell(cell_side * row, cell_side * col, (row, col))

def step_on_path():

    global carve_path
    if len(carve_path) > 0:
        can_be_carved = carve_path[-1].step()
        if not can_be_carved:
            carve_path[-1].reset_state()
            del carve_path[-1]
    else:
        global maze_done, target_node, start_node, open_list

        maze_done = True
        target_node = grid_matrix[-1][0].path_node_state()
        start_node = grid_matrix[0][-1].path_node_state()

        open_list.append(start_node)


# MAIN
pygame.init()
pygame.display.set_caption("Maze Gereration - Backtracking")
clock = pygame.time.Clock()

FPS = 30
cell_side = 60
screen_side = 600
cell_count_row, cell_count_col = (int(screen_side/cell_side), int(screen_side/cell_side))
grid_matrix = [[ None for i in range(cell_count_row)] for j in range(cell_count_col)]
carve_path = []
maze_done = False
path_found = False
do_path_animation = False

start_node = None
target_node = None
open_list = []
closed_list = []

screen = pygame.display.set_mode((screen_side, screen_side))

black_color = (0, 0, 0)
white_color = (255, 255, 255)
grey_color = (125, 125, 125)
red_color = (255, 100, 100)
teal_color = (100, 255, 255)
green_color = (100, 255, 100)

screen.fill(white_color)
init_cell_grid()
first = grid_matrix[randint(0, cell_count_row - 1)][randint(0, cell_count_col - 1)].being_carved_state()
carve_path.append(first)
draw_grid_matrix()

initial_time = time.time()
last_time = pygame.time.get_ticks()


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    if not maze_done:
        step_on_path()
    elif not path_found:
        pathfind()
    
    if path_found and not do_path_animation:
        find_final_path()
        do_path_animation = True

    screen.fill(white_color)
    draw_grid_matrix()
    pygame.display.update()
    clock.tick(FPS)