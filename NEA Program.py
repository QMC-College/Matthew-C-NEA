import pygame
import random
import sys
import time

pygame.init()

# Screen setup
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
CELL_SIZE = 50
columns = SCREEN_WIDTH // CELL_SIZE
rows = SCREEN_HEIGHT // CELL_SIZE
main_font = pygame.font.Font(None, 36)
running = False
state = "start"

# Pygame setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Algorithm Racer")
clock = pygame.time.Clock()


class Button():
    def __init__(self, image, x, y, button_text):
        self.image = image
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.button_text = button_text
        self.text = main_font.render(self.button_text, True, "white")
        self.text_rect = self.text.get_rect(center=(self.x, self.y))

    def update(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkinput(self, pos):
        return self.rect.collidepoint(pos)


class CellinMaze:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.visited = False
        self.walls = [True, True, True, True]  # Top, Right, Bottom, Left

    def draw(self, surface):
        x = self.x * self.size
        y = self.y * self.size
        if self.walls[0]:
            pygame.draw.line(surface, (255, 255, 255), (x, y), (x + self.size, y), 2)
        if self.walls[1]:
            pygame.draw.line(surface, (255, 255, 255), (x + self.size, y), (x + self.size, y + self.size), 2)
        if self.walls[2]:
            pygame.draw.line(surface, (255, 255, 255), (x + self.size, y + self.size), (x, y + self.size), 2)
        if self.walls[3]:
            pygame.draw.line(surface, (255, 255, 255), (x, y + self.size), (x, y), 2)


maze = []
for col in range(columns):
    column = []
    for row in range(rows):
        cell = CellinMaze(col, row, CELL_SIZE)
        column.append(cell)
    maze.append(column)
stack = []

def neighbour(cell):
    neighbours = []
    x = cell.x
    y = cell.y
    directions = [(-1, 0, 3, 1), (1, 0, 1, 3), (0, -1, 0, 2), (0, 1, 2, 0)]
    for x_change, y_change, wall, opposite_wall in directions:
        new_x = x + x_change
        new_y = y + y_change
        if 0 <= new_x < columns and 0 <= new_y < rows:
            neighbour = maze[new_x][new_y]
            if not neighbour.visited:
                neighbours.append((neighbour, wall, opposite_wall))
    return neighbours

def generate_maze():
    current = maze[0][0]
    current.visited = True
    stack.append(current)

    while len(stack) > 0:
        current = stack[-1]
        neighbours = neighbour(current)
        if len(neighbours) > 0:
            next_cell, wall, opposite_wall = random.choice(neighbours)
            current.walls[wall] = False
            next_cell.walls[opposite_wall] = False
            next_cell.visited = True
            stack.append(next_cell)
        else:
            stack.pop()

generate_maze()


class Finish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("apple.jpg").convert_alpha(), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        screen.blit(self.image, self.rect)

class User(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("user.jpg").convert_alpha(), (CELL_SIZE - 8, CELL_SIZE - 8))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x + 4, y + 4)
        self.grid_x = x // CELL_SIZE
        self.grid_y = y // CELL_SIZE

    def move(self, x_change, y_change):
        new_x = self.grid_x + x_change
        new_y = self.grid_y + y_change
        if 0 <= new_x < columns and 0 <= new_y < rows:
            cell = maze[self.grid_x][self.grid_y]
            if x_change == -1 and not cell.walls[3]:
                self.grid_x = new_x
            if x_change == 1 and not cell.walls[1]:
                self.grid_x = new_x
            if y_change == -1 and not cell.walls[0]:
                self.grid_y = new_y
            if y_change == 1 and not cell.walls[2]:
                self.grid_y = new_y
            self.rect.topleft = (self.grid_x * CELL_SIZE + 4, self.grid_y * CELL_SIZE + 4)

    def draw(self):
        screen.blit(self.image, self.rect.topleft)


user = User(0, 0)
finish = Finish((columns - 1) * CELL_SIZE, (rows - 1) * CELL_SIZE)

start_button = Button(pygame.transform.scale(pygame.image.load("start.png").convert_alpha(), (400, 150)),
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "")

play_again_button = Button(pygame.transform.scale(pygame.image.load("start.png").convert_alpha(), (400, 150)),
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 0.3*SCREEN_HEIGHT, "")


while state == "start":
    screen.fill((0, 0, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.checkinput(pygame.mouse.get_pos()):
                state = "game"
                running = True
                start_time = time.time()

    start_button.update()
    pygame.display.flip()
    clock.tick(60)



while running:
    screen.fill((100, 0, 100))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if state == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    user.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    user.move(1, 0)
                elif event.key == pygame.K_UP:
                    user.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    user.move(0, 1)
        elif state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.checkinput(pygame.mouse.get_pos()):
                    # Reset everything for a new game
                    maze.clear()
                    for col in range(columns):
                        column = []
                        for row in range(rows):
                            cell = CellinMaze(col, row, CELL_SIZE)
                            column.append(cell)
                        maze.append(column)
                    generate_maze()
                    user = User(0, 0)
                    finish = Finish((columns - 1) * CELL_SIZE, (rows - 1) * CELL_SIZE)
                    start_time = time.time()
                    state = "game"

    if state == "game":
        for col in maze:
            for cell in col:
                cell.draw(screen)

        finish.draw()
        user.draw()

        if user.rect.colliderect(finish.rect):
            state = "menu"
            end_time = time.time()
            total_time = end_time - start_time

    elif state == "menu":
        screen.fill((0, 200, 0))
        font = pygame.font.SysFont("Impact", 60)
        text = font.render("You Win!", True, (255, 255, 255))
        text2 = font.render(f"Total Time: {total_time:.3f}", True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - 0.18*SCREEN_WIDTH, SCREEN_HEIGHT // 2 - 0.4*SCREEN_HEIGHT))
        screen.blit(text2, (SCREEN_WIDTH // 2 - 0.31*SCREEN_WIDTH, SCREEN_HEIGHT // 2 -0.1*SCREEN_HEIGHT))
        play_again_button.update()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
