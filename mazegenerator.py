import pygame, sys
from random import randint, choice
from pygame.locals import *

def available(index):
    x = index[0]
    y = index[1]

    if x < 0 or  x > (cell_count_col - 1) or y < 0 or y > (cell_count_row - 1):
        return False
    
    if grid_matrix[x][y].activated == True:
        return False
    
    return True

class cell:
    def __init__(self, px, py, index):
        self.color = grey_color
        self.walls = [True, True, True, True]   #top, right, bottom and left
        self.rect = pygame.Rect(px, py, cell_w, cell_h)
        self.activated = False
        self.line_weight = 1
        self.index = index

    def draw(self):
        lw = self.line_weight
        pygame.draw.rect(screen, self.color, self.rect)

        if self.walls[0]:
            pygame.draw.rect(screen, black_color, (self.rect.left, self.rect.top, cell_w, lw))
        if self.walls[1]:
            pygame.draw.rect(screen, black_color, (self.rect.right - lw, self.rect.top, lw, cell_h))
        if self.walls[2]:
            pygame.draw.rect(screen, black_color, (self.rect.left, self.rect.bottom - lw, cell_w, lw))
        if self.walls[3]:
            pygame.draw.rect(screen, black_color, (self.rect.left, self.rect.top, lw, cell_h))

    def activate(self):
        self.activated = True
        self.color = red_color
        return self
    
    def deactivate(self):
        self.color = white_color

    def print_pos(self):
        print(self.index)

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
            carve_path[-1].activate()

            return True

def draw_grid_matrix():
    for row in range(cell_count_row):
        for col in range(cell_count_col):
            grid_matrix[row][col].draw()

def init_cell_grid():
    global grid_matrix
    for row in range(cell_count_row):
        for col in range(cell_count_col):
            grid_matrix[row][col] = cell(cell_w * row, cell_h * col, (row, col))

def step_on_path():

    global carve_path
    if len(carve_path) > 0:
        carved = carve_path[-1].step()
        if not carved:
            carve_path[-1].deactivate()
            del carve_path[-1]
    else:
        global maze_done
        maze_done = True

            


# MAIN
pygame.init()
pygame.display.set_caption("Maze Gereration - Backtracking")
clock = pygame.time.Clock()

cell_w, cell_h = (5, 5)
screen_w, screen_h = (500, 500)
cell_count_row, cell_count_col = (int(screen_w/cell_w), int(screen_h/cell_h))
grid_matrix = [[ None for i in range(cell_count_row)] for j in range(cell_count_col)]
carve_path = []
maze_done = False


screen = pygame.display.set_mode((screen_w, screen_h))

black_color = (0, 0, 0)
white_color = (255, 255, 255)
grey_color = (125, 125, 125)
red_color = (255, 100, 100)

screen.fill(white_color)
init_cell_grid()
first = grid_matrix[randint(0, cell_count_row - 1)][randint(0, cell_count_col - 1)].activate()
carve_path.append(first)
draw_grid_matrix()

while True:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                step_on_path()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    if not maze_done:
        step_on_path()

    screen.fill(white_color)
    draw_grid_matrix()
    pygame.display.update()
    clock.tick(30)