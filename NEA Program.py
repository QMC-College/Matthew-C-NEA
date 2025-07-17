import pygame
import random
import sys

pygame.init()
# Screen setup
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
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
# Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, image, size, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(image).convert_alpha(), (size, size))
        self.rect = self.image.get_rect(topleft=(x, y))

    def place(self):
        screen.blit(self.image, self.rect.topleft)

# Finish class
class Finish(pygame.sprite.Sprite):
    def __init__(self, image, size, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(image).convert_alpha(), (size, size))
        self.rect = self.image.get_rect(topleft=(x, y))

    def place(self):
        screen.blit(self.image, self.rect.topleft)

# User class
class User(pygame.sprite.Sprite):
    def __init__(self, image, width, height, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(image).convert_alpha(), (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = "None"
        self.prev_x = x
        self.prev_y = y

    def update(self):
        self.prev_x, self.prev_y = self.rect.x, self.rect.y
        if self.direction == "Left":
            self.rect.x -= 3
        elif self.direction == "Right":
            self.rect.x += 3
        elif self.direction == "Up":
            self.rect.y -= 3
        elif self.direction == "Down":
            self.rect.y += 3

    def revert_position(self):
        self.rect.x, self.rect.y = self.prev_x, self.prev_y

    def draw(self):
        screen.blit(self.image, self.rect.topleft)

# Create instances
walls = pygame.sprite.Group()
wall_positions = [
    (0, 0), (100, 0), (200, 0), (300, 0), (400, 0), (500, 0),
    (0, 200), (0, 300), (0, 400), (0, 500),
    (100, 500), (200, 500), (300, 500), (400, 500), (500, 500),
    (500, 400), (500, 300), (500, 100),
    (200, 200), (200, 300), (400, 300), (300, 0)
]
for pos in wall_positions:
    walls.add(Wall("wall.jpg", 100, *pos))

finish = Finish("apple.jpg", 100, 500, 200)
user = User("user.jpg", 92, 92, 100, 200)

# Main loop
running = True
state = "game"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    user.direction = "Left"
                elif event.key == pygame.K_RIGHT:
                    user.direction = "Right"
                elif event.key == pygame.K_UP:
                    user.direction = "Up"
                elif event.key == pygame.K_DOWN:
                    user.direction = "Down"
            elif event.type == pygame.KEYUP:
                user.direction = "None"

    if state == "game":
        screen.fill((100, 0, 255))
        user.update()

        # Collision with walls
        if pygame.sprite.spritecollideany(user, walls):
            user.revert_position()

        # Collision with finish
        if pygame.sprite.collide_rect(user, finish):
            state = "menu"

        # Draw everything
        for wall in walls:
            wall.place()
        finish.place()
        user.draw()

    elif state == "menu":
        screen.fill((255, 0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
