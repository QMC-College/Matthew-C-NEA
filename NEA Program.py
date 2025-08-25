import pygame
import random
import sys

pygame.init()
# Screen setup
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
CELL_SIZE = 50
columns = SCREEN_WIDTH // CELL_SIZE
rows = SCREEN_HEIGHT // CELL_SIZE

# Pygame setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Algorithm Racer")
clock = pygame.time.Clock()

class CellinMaze:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.visited = False
        self.walls = [True, True, True, True] #Checks all directionsfor neighbouring wall, in order Top, Right, Bottom, Left
    def draw(self, surface):
        x= self.x * self.size
        y = self.y * self.size # Fits to screen size
        # Check each direction for drawing, vectors created to show path and direction of travel
        if self.walls[0]:
            pygame.draw.line(surface, (255, 255, 255), (x, y), (x + self.size, y), 2)
        if self.walls[1]:
            pygame.draw.line(surface,(255,255,255), (x+self.size, y), (x +self.size, y + self.size), 2)
        if self.walls[2]:
            pygame.draw.line(surface, (255,255,255), (x+self.size, y+self.size)  , (x, y+self.size), 2)
        if self.walls[3]:
            pygame.draw.line(surface, (255,255,255), (x,y+self.size), (x,y), 2)
# Maze Generation
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
    x= cell.x
    y= cell.y
    directions = [(-1,0,3,1),(1,0,1,3),(0,-1,0,2), (0,1,2,0)]
    for x_change, y_change, wall, opposite_wall in directions:
        new_x = x + x_change
        new_y = y + y_change

        # Check if the new position is inside the maze
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
        current = stack[-1]  # Look at the last cell in the stack
        neighbours = neighbour(current)  # Find unvisited neighbors

        if len(neighbours) > 0:
            # Pick a random neighbor
            next_cell, wall, opposite_wall = random.choice(neighbours)

            # Remove the wall between current and next cell
            current.walls[wall] = False
            next_cell.walls[opposite_wall] = False

            # Mark the next cell as visited and add it to the stack
            next_cell.visited = True
            stack.append(next_cell)
        else:
            stack.pop()
generate_maze()


# Finish class
class Finish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("apple.jpg").convert_alpha(), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        screen.blit(self.image, self.rect)

# User class
class User(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("user.jpg").convert_alpha(), (CELL_SIZE - 8, CELL_SIZE - 8))
        self.rect = self.image.get_rect()
        self.direction = "None"
        self.prev_x = x
        self.prev_y = y
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

# Main loop
running = True
state = "game"

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

    # Draw Maze
    for col in maze:
        for cell in col:
            cell.draw(screen)

    # Draw Sprites
    finish.draw()
    user.draw()

    # Win Condition
    if user.rect.colliderect(finish.rect):
        state = "menu"

    if state == "menu":
        screen.fill((0, 200, 0))
        font = pygame.font.SysFont(None, 60)
        text = font.render("You Win!", True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
