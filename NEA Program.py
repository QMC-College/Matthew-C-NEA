import pygame
import random
import sys
import time
import heapq

pygame.init()
start_time = 0

#Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 80
columns = SCREEN_WIDTH // CELL_SIZE
rows = SCREEN_HEIGHT // CELL_SIZE
main_font = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Algorithm Racer")
clock = pygame.time.Clock()

#Game state
running = True
state = "start"
name_submitted = False
current_algorithm = None
winner = None
total_time = 0

#Algorithm delays (frames)
DFS_DELAY = 15
BFS_DELAY = 15
DIJKSTRA_DELAY = 15

#Classes
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
            pygame.draw.line(surface, (255,255,255), (x, y), (x+self.size, y), 2)
        if self.walls[1]:
            pygame.draw.line(surface, (255,255,255), (x+self.size, y), (x+self.size, y+self.size), 2)
        if self.walls[2]:
            pygame.draw.line(surface, (255,255,255), (x+self.size, y+self.size), (x, y+self.size), 2)
        if self.walls[3]:
            pygame.draw.line(surface, (255,255,255), (x, y+self.size), (x, y), 2)

class User(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images/user.jpg").convert_alpha(), (CELL_SIZE-8, CELL_SIZE-8))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x+4, y+4)
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
            self.rect.topleft = (self.grid_x*CELL_SIZE+4, self.grid_y*CELL_SIZE+4)
    def draw(self):
        screen.blit(self.image, self.rect.topleft)

class Finish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images/apple.jpg").convert_alpha(), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    def draw(self):
        screen.blit(self.image, self.rect)

class TextBox:
    def __init__(self, x, y, w, h, font, max_length=12):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (180, 180, 180)
        self.color_active = (255, 255, 255)
        self.color = self.color_inactive
        self.font = font
        self.text = ""
        self.active = False
        self.max_length = max_length
        self.submitted = False
    def handle_event(self, event):
        if self.submitted:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self.color = self.color_active
            else:
                self.color = self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.submitted = True
                self.active = False
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length:
                self.text += event.unicode
        return None
    def draw(self):
        txt_surface = self.font.render(self.text, True, (0,0,0))
        width = max(self.rect.w, txt_surface.get_width()+10)
        self.rect.w = width
        screen.blit(txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

#Maze generation
maze = []
for x in range(columns):
    column = []
    for y in range(rows):
        column.append(CellinMaze(x, y, CELL_SIZE))
    maze.append(column)

stack = []

def neighbour(cell):
    neighbours = []
    x = cell.x
    y = cell.y
    directions = [(-1,0,3,1),(1,0,1,3),(0,-1,0,2),(0,1,2,0)]
    for change_x, change_y, wall, opp in directions:
        nx = x + change_x
        ny = y + change_y
        if 0 <= nx < columns and 0 <= ny < rows:
            neighbor_cell = maze[nx][ny]
            if not neighbor_cell.visited:
                neighbours.append((neighbor_cell, wall, opp))
    return neighbours

def generate_maze():
    current = maze[0][0]
    current.visited = True
    stack.append(current)
    while len(stack) > 0:
        current = stack[-1]
        n = neighbour(current)
        if len(n) > 0:
            next_cell, wall, opp = random.choice(n)
            current.walls[wall] = False
            next_cell.walls[opp] = False
            next_cell.visited = True
            stack.append(next_cell)
        else:
            stack.pop()

generate_maze()

#Leaderboard
def text_file(name, time_value):
    with open("leaderboard.txt", "a") as f:
        f.write(f"{name},{time_value:.3f}\n")

def read_leaderboard():
    scores = []
    try:
        with open("leaderboard.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    try:
                        scores.append((parts[0], float(parts[1])))
                    except:
                        pass
        scores.sort(key=lambda x:x[1])
    except:
        pass
    return scores

#Algorithm Racer
class AlgorithmRacer:
    def __init__(self, algo, start_cell, goal_cell):
        self.algo = algo
        self.start = start_cell
        self.goal = goal_cell
        self.visited = set()
        self.prev = {}
        self.path = []
        self.path_found = False
        self.frame_counter = 0
        if algo == "DFS":
            self.frontier = [start_cell]
        elif algo == "BFS":
            self.frontier = [start_cell]
        elif algo == "Dijkstra":
            self.frontier = []
            heapq.heappush(self.frontier,(0,start_cell))
            self.dist = {start_cell:0}

    def step(self):
        if self.path_found or len(self.frontier) == 0:
            return

        # Delay frame counter
        if self.algo == "DFS":
            delay = DFS_DELAY
        elif self.algo == "BFS":
            delay = BFS_DELAY
        else:
            delay = DIJKSTRA_DELAY

        self.frame_counter += 1
        if self.frame_counter < delay:
            return
        self.frame_counter = 0

        # Pop next cell
        if self.algo == "DFS":
            current = self.frontier.pop()
        elif self.algo == "BFS":
            current = self.frontier.pop(0)
        else:
            _, current = heapq.heappop(self.frontier)

        if current in self.visited:
            return

        self.visited.add(current)

        if current == self.goal:
            self.reconstruct_path()
            self.path_found = True
            return

        neighbors = get_neighbors(current)
        for neighbor in neighbors:
            if neighbor not in self.visited:
                if self.algo in ["DFS","BFS"] and neighbor not in self.frontier:
                    self.frontier.append(neighbor)
                    self.prev[neighbor] = current
                elif self.algo == "Dijkstra":
                    new_dist = self.dist[current] + 1
                    if neighbor not in self.dist or new_dist < self.dist[neighbor]:
                        self.dist[neighbor] = new_dist
                        heapq.heappush(self.frontier,(new_dist,neighbor))
                        self.prev[neighbor] = current

    def reconstruct_path(self):
        self.path = []
        cell = self.goal
        while cell in self.prev:
            self.path.append(cell)
            cell = self.prev[cell]
        self.path.append(self.start)
        self.path.reverse()

    def draw(self):
        for cell in self.visited:
            pygame.draw.rect(screen,(0,255,255),(cell.x*CELL_SIZE+10, cell.y*CELL_SIZE+10, CELL_SIZE-20, CELL_SIZE-20))
        for cell in self.path:
            pygame.draw.rect(screen,(255,0,0),(cell.x*CELL_SIZE+20, cell.y*CELL_SIZE+20, CELL_SIZE-40, CELL_SIZE-40))

def get_neighbors(cell):
    x, y = cell.x, cell.y
    neighbors = []
    directions = [(-1,0,3,1),(1,0,1,3),(0,-1,0,2),(0,1,2,0)]
    for change_x, change_y, wall, opp in directions:
        nx = x + change_x
        ny = y + change_y
        if 0 <= nx < columns and 0 <= ny < rows:
            if not cell.walls[wall] and not maze[nx][ny].walls[opp]:
                neighbors.append(maze[nx][ny])
    return neighbors

#Buttons
start_button = Button(pygame.transform.scale(pygame.image.load("images/start.png").convert_alpha(), (400,150)), SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "")
play_again_button = Button(pygame.transform.scale(pygame.image.load("images/replay.png").convert_alpha(), (250,80)), SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40, "")
leaderboard_button = Button(pygame.transform.scale(pygame.image.load("images/scores.png").convert_alpha(), (250,80)), SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 140, "")
back_button = Button(pygame.transform.scale(pygame.image.load("images/menu.png").convert_alpha(), (200,70)), SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, "")

#Initialize User/Finish
user = User(0,0)
finish = Finish((columns-1)*CELL_SIZE,(rows-1)*CELL_SIZE)
name_box = TextBox(SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2+60, 200,50,pygame.font.SysFont("Arial",40))

#Start Screen
while state == "start":
    screen.fill((0,0,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.checkinput(pygame.mouse.get_pos()):
                state = "algorithm_select"
    start_button.update()
    pygame.display.flip()
    clock.tick(60)

#Algorithm Selection
dfs_button = Button(pygame.Surface((250,80)), SCREEN_WIDTH//2, SCREEN_HEIGHT//2-100, "DFS")
bfs_button = Button(pygame.Surface((250,80)), SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "BFS")
dijkstra_button = Button(pygame.Surface((250,80)), SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100, "Dijkstra")

while state == "algorithm_select":
    screen.fill((0,100,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if dfs_button.checkinput(pos):
                current_algorithm = "DFS"
                state = "race"
            elif bfs_button.checkinput(pos):
                current_algorithm = "BFS"
                state = "race"
            elif dijkstra_button.checkinput(pos):
                current_algorithm = "Dijkstra"
                state = "race"
    dfs_button.update()
    bfs_button.update()
    dijkstra_button.update()
    pygame.display.flip()
    clock.tick(60)

#Initialize Racer
racer = AlgorithmRacer(current_algorithm, maze[0][0], maze[columns-1][rows-1])
start_time = 0

#Main Loop
while running:

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if state == "race" and event.type == pygame.KEYDOWN:
            if start_time == 0:
                start_time = time.time()
            if event.key == pygame.K_LEFT:
                user.move(-1,0)
            elif event.key == pygame.K_RIGHT:
                user.move(1,0)
            elif event.key == pygame.K_UP:
                user.move(0,-1)
            elif event.key == pygame.K_DOWN:
                user.move(0,1)
        if state == "menu":
            result = name_box.handle_event(event)
            if result is not None and not name_submitted:
                player_name = result if result.strip() != "" else "Anonymous"
                text_file(player_name, total_time)
                name_submitted = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_again_button.checkinput(mouse_pos):
                    # Reset maze and race
                    maze = []
                    for x in range(columns):
                        column = []
                        for y in range(rows):
                            column.append(CellinMaze(x, y, CELL_SIZE))
                        maze.append(column)
                    generate_maze()
                    user = User(0, 0)
                    finish = Finish((columns-1)*CELL_SIZE,(rows-1)*CELL_SIZE)
                    racer = AlgorithmRacer(current_algorithm, maze[0][0], maze[columns-1][rows-1])
                    start_time = 0
                    name_submitted = False
                    winner = None
                    state = "race"
                elif leaderboard_button.checkinput(mouse_pos):
                    state = "leaderboard"
        if state == "leaderboard":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkinput(pygame.mouse.get_pos()):
                    state = "menu"

    #Race Logic
    if state == "race":
        screen.fill((0,0,0))
        for x in range(columns):
            for y in range(rows):
                maze[x][y].draw(screen)
        finish.draw()
        user.draw()
        if winner is None:
            racer.step()
        racer.draw()
        # Check winner
        if user.rect.colliderect(finish.rect) and winner is None:
            winner = "You"
            total_time = time.time() - start_time
            state = "menu"
        elif racer.path_found and winner is None:
            winner = current_algorithm
            total_time = time.time() - start_time
            state = "menu"

    #Menu
    elif state == "menu":
        screen.fill((0,200,0))
        font_big = pygame.font.SysFont("Impact", 60)
        font_small = pygame.font.SysFont("Arial", 40)
        if winner is not None:
            screen.blit(font_big.render(f"{winner} Won!", True, (255,255,255)), (SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2-200))
            screen.blit(font_small.render(f"Time: {total_time:.3f}", True, (255,255,255)), (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2-140))
        name_box.draw()
        play_again_button.update()
        leaderboard_button.update()

    #Leaderboard
    elif state == "leaderboard":
        screen.fill((0,0,0))
        font_title = pygame.font.SysFont("Impact",60)
        font_entry = pygame.font.SysFont("Arial",30)
        screen.blit(font_title.render("Leaderboard", True, (255,215,0)), (SCREEN_WIDTH//2-150,50))
        y_offset = 120
        scores = read_leaderboard()
        if len(scores) == 0:
            screen.blit(font_entry.render("No scores yet!", True, (255,255,255)), (100, y_offset))
        else:
            for count, score in enumerate(scores[:15],1):
                screen.blit(font_entry.render(f"{count}. {score[0]} - {score[1]:.3f} s", True, (255,255,255)), (50, y_offset))
                y_offset += 35
        back_button.update()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
