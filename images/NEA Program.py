import pygame
import random
import sys
import time
import heapq

pygame.init()
start_time = 0

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 80
columns = SCREEN_WIDTH // CELL_SIZE
rows = SCREEN_HEIGHT // CELL_SIZE
main_font = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Algorithm Racer")
clock = pygame.time.Clock()

running = True
state = "start"
name_submitted = False
current_algorithm = None
winner = None
total_time = 0

DFS_DELAY = 15
BFS_DELAY = 15
DIJKSTRA_DELAY = 15


# ---------------- GUI CLASSES ----------------

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
            self.color = self.color_active if self.active else self.color_inactive
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
        self.rect.w = max(self.rect.w, txt_surface.get_width()+10)
        screen.blit(txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


# ---------------- MAZE ----------------

class MazeCell:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.visited = False
        self.walls = [True, True, True, True]  # Top, Right, Bottom, Left

    def draw(self, surface):
        px = self.x * self.size
        py = self.y * self.size
        if self.walls[0]:
            pygame.draw.line(surface, (255,255,255), (px, py), (px+self.size, py), 2)
        if self.walls[1]:
            pygame.draw.line(surface, (255,255,255), (px+self.size, py), (px+self.size, py+self.size), 2)
        if self.walls[2]:
            pygame.draw.line(surface, (255,255,255), (px+self.size, py+self.size), (px, py+self.size), 2)
        if self.walls[3]:
            pygame.draw.line(surface, (255,255,255), (px, py+self.size), (px, py), 2)


maze = []
for x in range(columns):
    column = []
    for y in range(rows):
        column.append(MazeCell(x, y, CELL_SIZE))
    maze.append(column)

stack = []


def neighbour(cell):
    neighbours = []
    directions = [(-1,0,3,1),(1,0,1,3),(0,-1,0,2),(0,1,2,0)]
    for dx, dy, wall, opp in directions:
        nx = cell.x + dx
        ny = cell.y + dy
        if 0 <= nx < columns and 0 <= ny < rows:
            next_cell = maze[nx][ny]
            if not next_cell.visited:
                neighbours.append((next_cell, wall, opp))
    return neighbours


def generate_maze():
    current = maze[0][0]
    current.visited = True
    stack.append(current)
    while stack:
        current = stack[-1]
        n = neighbour(current)
        if n:
            next_cell, wall, opp = random.choice(n)
            current.walls[wall] = False
            next_cell.walls[opp] = False
            next_cell.visited = True
            stack.append(next_cell)
        else:
            stack.pop()


generate_maze()


# ---------------- GRID OBJECT INHERITANCE ----------------

class GridObject(pygame.sprite.Sprite):
    def __init__(self, grid_x, grid_y, image_path, offset=0):
        super().__init__()
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.offset = offset
        self.image = pygame.transform.scale(
            pygame.image.load(image_path).convert_alpha(),
            (CELL_SIZE - offset*2, CELL_SIZE - offset*2)
        )
        self.rect = self.image.get_rect()
        self.update_rect()

    def update_rect(self):
        self.rect.topleft = (
            self.grid_x * CELL_SIZE + self.offset,
            self.grid_y * CELL_SIZE + self.offset
        )

    def draw(self):
        screen.blit(self.image, self.rect)


class User(GridObject):
    def __init__(self, x, y):
        super().__init__(x // CELL_SIZE, y // CELL_SIZE, "user.jpg", offset=4)

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
            self.update_rect()


class Finish(GridObject):
    def __init__(self, x, y):
        super().__init__(x // CELL_SIZE, y // CELL_SIZE, "apple.jpg")


# ---------------- DATA MANAGEMENT ----------------

def text_file(name, time_value):
    with open("leaderboard.txt", "a") as f:
        f.write(f"{name},{time_value:.3f}\n")


def read_leaderboard():
    scores = []
    try:
        with open("leaderboard.txt", "r") as f:
            for line in f:
                name, t = line.strip().split(",")
                scores.append((name, float(t)))
        scores.sort(key=lambda x: x[1])
    except:
        pass
    return scores


# ---------------- PATHFINDING ----------------

def get_neighbors(cell):
    neighbors = []
    directions = [(-1,0,3,1),(1,0,1,3),(0,-1,0,2),(0,1,2,0)]
    for dx, dy, wall, opp in directions:
        nx = cell.x + dx
        ny = cell.y + dy
        if 0 <= nx < columns and 0 <= ny < rows:
            if not cell.walls[wall] and not maze[nx][ny].walls[opp]:
                neighbors.append(maze[nx][ny])
    return neighbors


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

        if algo == "Dijkstra":
            self.frontier = []
            heapq.heappush(self.frontier, (0, start_cell))
            self.dist = {start_cell: 0}
        else:
            self.frontier = [start_cell]

    def step(self):
        if self.path_found or not self.frontier:
            return

        delay = DFS_DELAY if self.algo == "DFS" else BFS_DELAY if self.algo == "BFS" else DIJKSTRA_DELAY
        self.frame_counter += 1
        if self.frame_counter < delay:
            return
        self.frame_counter = 0

        current = (
            self.frontier.pop() if self.algo == "DFS"
            else self.frontier.pop(0) if self.algo == "BFS"
            else heapq.heappop(self.frontier)[1]
        )

        if current in self.visited:
            return

        self.visited.add(current)

        if current == self.goal:
            self.reconstruct_path()
            self.path_found = True
            return

        for neighbor in get_neighbors(current):
            if neighbor not in self.visited:
                if self.algo in ["DFS", "BFS"] and neighbor not in self.frontier:
                    self.frontier.append(neighbor)
                    self.prev[neighbor] = current
                elif self.algo == "Dijkstra":
                    new_dist = self.dist[current] + 1
                    if neighbor not in self.dist or new_dist < self.dist[neighbor]:
                        self.dist[neighbor] = new_dist
                        heapq.heappush(self.frontier, (new_dist, neighbor))
                        self.prev[neighbor] = current

    def reconstruct_path(self):
        cell = self.goal
        while cell in self.prev:
            self.path.append(cell)
            cell = self.prev[cell]
        self.path.append(self.start)
        self.path.reverse()

    def draw(self):
        for cell in self.visited:
            pygame.draw.rect(screen, (0,0,255),
                (cell.x*CELL_SIZE+10, cell.y*CELL_SIZE+10, CELL_SIZE-20, CELL_SIZE-20))
        for cell in self.path:
            pygame.draw.rect(screen, (255,255,0),
                (cell.x*CELL_SIZE+20, cell.y*CELL_SIZE+20, CELL_SIZE-40, CELL_SIZE-40))


# ---------------- UI OBJECTS ----------------

start_button = Button(pygame.transform.scale(pygame.image.load("start.png").convert_alpha(), (400,150)),
                      SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "")
play_again_button = Button(pygame.transform.scale(pygame.image.load("replay.png").convert_alpha(), (250,80)),
                           SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40, "")
leaderboard_button = Button(pygame.transform.scale(pygame.image.load("scores.png").convert_alpha(), (250,80)),
                            SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 140, "")
back_button = Button(pygame.transform.scale(pygame.image.load("menu.png").convert_alpha(), (200,70)),
                     SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, "")

user = User(0, 0)
finish = Finish((columns-1)*CELL_SIZE, (rows-1)*CELL_SIZE)
name_box = TextBox(SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2+60, 200, 50, pygame.font.SysFont("Arial",40))


# ---------------- GAME STATES ----------------

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


racer = AlgorithmRacer(current_algorithm, maze[0][0], maze[columns-1][rows-1])
start_time = 0


while running:
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
                player_name = result if result.strip() else "Anonymous"
                text_file(player_name, total_time)
                name_submitted = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if play_again_button.checkinput(pos):
                    maze = [[MazeCell(x, y, CELL_SIZE) for y in range(rows)] for x in range(columns)]
                    generate_maze()
                    user = User(0, 0)
                    finish = Finish((columns-1)*CELL_SIZE, (rows-1)*CELL_SIZE)
                    racer = AlgorithmRacer(current_algorithm, maze[0][0], maze[columns-1][rows-1])
                    start_time = 0
                    name_submitted = False
                    winner = None
                    state = "race"
                elif leaderboard_button.checkinput(pos):
                    state = "leaderboard"

        if state == "leaderboard" and event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.checkinput(pygame.mouse.get_pos()):
                state = "menu"

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

        if user.rect.colliderect(finish.rect) and winner is None:
            winner = "You"
            total_time = time.time() - start_time
            state = "menu"
        elif racer.path_found and winner is None:
            winner = current_algorithm
            total_time = time.time() - start_time
            state = "menu"

    elif state == "menu":
        screen.fill((0,200,0))
        font_big = pygame.font.SysFont("Impact", 60)
        font_small = pygame.font.SysFont("Arial", 40)
        if winner:
            screen.blit(font_big.render(f"{winner} Won!", True, (255,255,255)),
                        (SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2-200))
            screen.blit(font_small.render(f"Time: {total_time:.3f}", True, (255,255,255)),
                        (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2-140))
        name_box.draw()
        play_again_button.update()
        leaderboard_button.update()

    elif state == "leaderboard":
        screen.fill((0,0,0))
        font_title = pygame.font.SysFont("Impact",60)
        font_entry = pygame.font.SysFont("Arial",30)
        screen.blit(font_title.render("Leaderboard", True, (255,215,0)),
                    (SCREEN_WIDTH//2-150,50))
        y = 120
        scores = read_leaderboard()
        if not scores:
            screen.blit(font_entry.render("No scores yet!", True, (255,255,255)), (100, y))
        else:
            for i, score in enumerate(scores[:15],1):
                screen.blit(font_entry.render(f"{i}. {score[0]} - {score[1]:.3f} s",
                           True, (255,255,255)), (50, y))
                y += 35
        back_button.update()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
