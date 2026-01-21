import pygame
import random
import sys
import time
import heapq

class AlgorithmRacer:
    def __init__(self, algo):
        # Which algorithm this racer is using (BFS, DFS, Dijkstra)
        self.algo = algo

        # Marks start and goal cells
        self.start = maze[0][0]
        self.goal = maze[columns - 1][rows - 1]


        self.visited = set()
        self.prev = {}
        self.path = []

        self.frame = 0

        # Current cell the AI is processing
        self.current = self.start


        self.dead_ends = set()

        # Frontier setup depends on algorithm
        if algo == "Dijkstra":
            self.frontier = []
            heapq.heappush(self.frontier, (0, 0, self.start)) # Priority Queue Setup

            self.dist = {self.start: 0}
            self.counter = 0 # IMPORTANT - Exists to break equalities in heap distance
        else:
            self.frontier = [self.start]

    def reconstruct_path(self, target=None):
        """
        Builds a path from the start cell to either:
        - the goal cell
        - OR the current cell (for AI Route viewing)
        """
        self.path = []

        # Decide where to stop the path
        if target is not None:
            current_cell = target
        else:
            current_cell = self.goal
        # Recursive Backtracking Aspect
        while current_cell in self.prev:
            self.path.append(current_cell) # Prev Dictionary creates a backwards path
            current_cell = self.prev[current_cell]

        self.path.append(self.start)
        self.path.reverse()

    def step(self):
        # Control animation speed
        self.frame += 1
        if self.frame < delay:
            return

        if not self.frontier:
            return

        self.frame = 0

        
        if self.algo == "DFS":
            current = self.frontier.pop() # DFS takes last (stack)

        elif self.algo == "BFS":
            current = self.frontier.pop(0) # BFS takes first (queue)

        else:  # Dijkstra
            item = heapq.heappop(self.frontier)
            current = item[2] # finding cell out of heap

        self.current = current

        # Skip already visited cells
        if current in self.visited:
            return

        self.visited.add(current)

        # If goal reached, lock in final path
        if current == self.goal:
            self.reconstruct_path(self.goal)
            return
        else:
            # Otherwise, update path to current position
            self.reconstruct_path(self.current)

        expanded = False # Important - Checks whether current cell led to any new paths

        # Explore neighbours
        for neighbour in get_neighbors(current):

            if self.algo == "Dijkstra":
                new_distance = self.dist[current] + 1

                if neighbour not in self.dist or new_distance < self.dist[neighbour]: # Only updates if path is shorter than previous paths
                    self.dist[neighbour] = new_distance
                    self.counter += 1

                    heapq.heappush(self.frontier,(new_distance, self.counter, neighbour)) # Adding neighbour to priority queue

                    self.prev[neighbour] = current
                    expanded = True

            else: #BFS and DFS
                if neighbour not in self.visited and neighbour not in self.frontier: # Only adds unvisited cells not waiting in frontier
                    self.frontier.append(neighbour)
                    self.prev[neighbour] = current
                    expanded = True

        # Mark dead ends if it doesn't lead anywhere
        if not expanded and current != self.goal:
            self.dead_ends.add(current)

    def draw(self):
        # Draw explored cells
        for cell in self.visited:
            if cell in self.dead_ends:
                colour = (130, 130, 130)
            else:
                colour = (0, 0, 150)

            pygame.draw.rect(screen,colour,(cell.x * CELL_SIZE + 10,cell.y * CELL_SIZE + 10,CELL_SIZE - 20,CELL_SIZE - 20))

        # Draw path (lines + dots)
        for i in range(len(self.path) - 1):
            c1 = self.path[i]
            c2 = self.path[i + 1]

            x1 = c1.x * CELL_SIZE + CELL_SIZE // 2
            y1 = c1.y * CELL_SIZE + CELL_SIZE // 2
            x2 = c2.x * CELL_SIZE + CELL_SIZE // 2
            y2 = c2.y * CELL_SIZE + CELL_SIZE // 2

            pygame.draw.circle(screen, (255, 0, 0), (x1, y1), 5)
            pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 3)

        # Draw final position dot
        if self.path:
            last = self.path[-1]
            pygame.draw.circle(screen,(0, 0, 255),(last.x * CELL_SIZE + CELL_SIZE // 2,last.y * CELL_SIZE + CELL_SIZE // 2),10)

        return len(self.path)
class Button:
    def __init__(self, surf, x, y, text):
        self.image = surf
        self.rect = surf.get_rect(center=(x, y))
        self.text = main_font.render(text, True, "white")
        self.text_rect = self.text.get_rect(center=(x, y))

    def draw(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def check(self, pos):
        return self.rect.collidepoint(pos) # recognises collisions with mouse

class Slider:
    def __init__(self, x, y, w, min_v, max_v, start):
        self.rect = pygame.Rect(x, y, w, 6)
        self.min = min_v
        self.max = max_v
        self.value = start
        self.handle_x = x + (start - min_v) / (max_v - min_v) * w
        self.drag = False

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            if abs(e.pos[0] - self.handle_x) < 12: # abs() gives distance without worrying about left/right
                self.drag = True
        elif e.type == pygame.MOUSEBUTTONUP:
            self.drag = False
        elif e.type == pygame.MOUSEMOTION and self.drag:
            self.handle_x = max(self.rect.left, min(e.pos[0], self.rect.right))
            self.value = int(self.min + (self.handle_x - self.rect.left) / self.rect.width * (self.max - self.min)) # calculation to work out position of slider

    def draw(self):
        pygame.draw.rect(screen, (180,180,180), self.rect)
        pygame.draw.circle(screen, (50,50,50), (int(self.handle_x), self.rect.centery), 10)

# ---------------- MAZE CREATION----------------
class GridObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pass  # Will be overridden by subclasses
class Cell(GridObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.visited = False
        self.walls = [True, True, True, True]

    def draw(self):
        px = self.x*CELL_SIZE
        py = self.y*CELL_SIZE
        if self.walls[0]:
            pygame.draw.line(screen,(255,255,255),(px,py),(px+CELL_SIZE,py),2)
        if self.walls[1]:
            pygame.draw.line(screen,(255,255,255),(px+CELL_SIZE,py),(px+CELL_SIZE,py+CELL_SIZE),2)
        if self.walls[2]:
            pygame.draw.line(screen,(255,255,255),(px+CELL_SIZE,py+CELL_SIZE),(px,py+CELL_SIZE),2)
        if self.walls[3]:
            pygame.draw.line(screen,(255,255,255),(px,py+CELL_SIZE),(px,py),2)

class ImageObject(GridObject):
    def __init__(self, x, y, image_path, size_offset=0):
        super().__init__(x, y)
        # Load and scale the image
        self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(),(CELL_SIZE - size_offset, CELL_SIZE - size_offset))
        self.rect = self.image.get_rect(topleft=(self.x*CELL_SIZE, self.y*CELL_SIZE))

    def update_rect(self):
        self.rect.topleft = (self.x*CELL_SIZE, self.y*CELL_SIZE)

    def draw(self):
        screen.blit(self.image, self.rect)
class User(ImageObject):
    def __init__(self):
        super().__init__(0,0,"images/user.jpg", size_offset = 8)
        self.image = pygame.transform.scale(pygame.image.load("images/user.jpg").convert_alpha(),(CELL_SIZE-8, CELL_SIZE-8))


    def move(self, dx, dy):
        cell = maze[self.x][self.y]
        if dx == -1 and not cell.walls[3]:
            self.x -= 1
        if dx == 1 and not cell.walls[1]:
            self.x += 1
        if dy == -1 and not cell.walls[0]:
            self.y -= 1
        if dy == 1 and not cell.walls[2]:
            self.y += 1
        self.update_rect() # Keeps rect in sync


class Finish(ImageObject):
    def __init__(self):
        super().__init__(columns-1, rows-1, "images/apple.jpg")
# ---------------- LEADERBOARDS ----------------
def leaderboard_file():
    return f"leaderboard_{maze_size}x{maze_size}.txt"

def save_score(name, time_value):
    with open(leaderboard_file(), "a") as f:
        f.write(f"{name},{time_value:.3f}\n")

def read_leaderboard():
    scores = []
    try:
        with open(leaderboard_file(), "r") as f:
            for line in f:
                n, t = line.strip().split(",")
                scores.append((n, float(t)))
        scores.sort(key=lambda x: x[1]) # sorts by time
    except:
        pass
    return scores

# ---------------- UI ----------------


def generate_maze():
    stack = []
    current = maze[0][0]
    current.visited = True
    stack.append(current)
    directions = [(-1,0,3,1),(1,0,1,3),(0,-1,0,2),(0,1,2,0)] # Left, Right, Up, Down
    while stack:
        current = stack[-1]
        unvisited = []
        for change_x,change_y,wall,opposite_wall in directions:
            newx = current.x + change_x
            newy = current.y + change_y
            if 0 <= newx < columns and 0 <= newy < rows and not maze[newx][newy].visited: # Checks neighbour is in bounds and unvisited
                neighbour = maze[newx][newy]
                unvisited.append((neighbour, wall, opposite_wall))
        if unvisited:
            next_cell,wall,opposite_wall = random.choice(unvisited)
            current.walls[wall] = False
            next_cell.walls[opposite_wall] = False
            next_cell.visited = True
            stack.append(next_cell)
        else:
            stack.pop() # Backtrack if no unvisited neighbours


def rebuild_maze(size):
    global maze_size, CELL_SIZE, columns, rows, maze, user, finish, racer

    maze_size = size
    CELL_SIZE = SCREEN_WIDTH // maze_size
    columns = rows = maze_size

    maze = [[Cell(x, y) for y in range(rows)] for x in range(columns)]
    generate_maze()

    user = User()
    finish = Finish()
    
    racer = None
def reset_game():
    global maze, user, finish, racer, winner, start_time, ai_started, score_saved, random_controls, control_map

    for x in range(columns):
        for y in range(rows):
            maze[x][y].visited = False
            maze[x][y].walls = [True, True, True, True]

    generate_maze()

    user = User()
    finish = Finish()
    ai_started = False
    racer = None
    winner = None
    start_time = 0
    score_saved = False
    random_controls = False
    control_map = {}





def get_neighbors(cell):
    neighbours = []
    directions = [(-1,0,3,1),(1,0,1,3),(0,-1,0,2),(0,1,2,0)]
    for change_x,change_y,wall,opposite_wall in directions:
        newx = cell.x+change_x
        newy = cell.y+change_y
        if 0 <= newx < columns and 0 <= newy < rows:
            if not cell.walls[wall]:
                neighbours.append(maze[newx][newy])
    return neighbours


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
maze_size = 10
CELL_SIZE = SCREEN_WIDTH // maze_size
columns = SCREEN_WIDTH // CELL_SIZE
rows = SCREEN_HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Algorithm Racer")
clock = pygame.time.Clock()

main_font = pygame.font.SysFont("OCR A EXTENDED", 50)
font_small = pygame.font.SysFont("OCR A EXTENDED", 32)
font_big = pygame.font.SysFont("OCR A EXTENDED", 60)

running = True
state = "start"

current_algorithm = None
algorithm_selected = False
difficulty_selected = False
delay = 30
ai_started = False
score_saved = False
winner = None
start_time = 0
total_time = 0
just_started = False
player_name = ""
name_active = False
name_submitted = False
random_controls = False
control_map = {}

maze = [[Cell(x,y) for y in range(rows)] for x in range(columns)]
user = User()
finish = Finish()
generate_maze()
btn = pygame.Surface((300,70))
btn.fill((60,60,60))
c = pygame.Surface((180,70))
c.fill((50,50,50))


start_button = Button(btn,400,300,"START")
difficulty_button = Button(btn,400,400,"SELECT AI")

bfs_button = Button(btn,400,120,"BFS (Easy)")
dfs_button = Button(btn,400,280,"DFS (Hard)")
dijkstra_button = Button(btn,400,200,"DIJKSTRA (Medium)")
size5_btn  = Button(c, 100, 520, "5x5")
size8_btn  = Button(c, 300, 520, "8x8")
size10_btn = Button(c, 500, 520, "10x10")
size20_btn = Button(c, 700, 520, "20x20")
random_button = Button(btn, 700, 100, "??? OFF")
back_button = Button(btn,400,650,"BACK")
leaderboard_button = Button(btn,400,560,"LEADERBOARD")
view_route_button = Button(btn, 400, 460, "VIEW AI ROUTE")

slider = Slider(250,380,300,1,60,30)

racer = None

# ---------------- MAIN LOOP ----------------

while running:
    # ------------------- EVENT HANDLING -------------------
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        # ---------------- START SCREEN ----------------
        if state == "start" and e.type == pygame.MOUSEBUTTONDOWN:
            if difficulty_button.check(e.pos):
                state = "difficulty"
            elif start_button.check(e.pos) and difficulty_selected and algorithm_selected:
                racer = AlgorithmRacer(current_algorithm)
                start_time = time.time()
                just_started = True
                if random_controls:
                    keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
                    shuffled = keys[:]
                    random.shuffle(shuffled)
                    control_map = {
                        pygame.K_UP: shuffled[0],
                        pygame.K_DOWN: shuffled[1],
                        pygame.K_LEFT: shuffled[2],
                        pygame.K_RIGHT: shuffled[3]
                    }
                else:
                    control_map = {}
                state = "race"
                ai_started = False
                score_saved = False

        # ---------------- DIFFICULTY SCREEN ----------------
        if state == "difficulty":
            slider.handle_event(e)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if bfs_button.check(e.pos):
                    current_algorithm = "BFS"
                    algorithm_selected = True
                elif dfs_button.check(e.pos):
                    current_algorithm = "DFS"
                    algorithm_selected = True
                elif dijkstra_button.check(e.pos):
                    current_algorithm = "Dijkstra"
                    algorithm_selected = True
                elif back_button.check(e.pos):
                    delay = max(1, 60 - slider.value)
                    difficulty_selected = True
                    state = "start"
                elif size5_btn.check(e.pos):
                    rebuild_maze(5)
                elif size8_btn.check(e.pos):
                    rebuild_maze(8)
                elif size10_btn.check(e.pos):
                    rebuild_maze(10)
                elif size20_btn.check(e.pos):
                    rebuild_maze(20)
                elif random_button.check(e.pos):
                    random_controls = not random_controls

        # ---------------- RACE SCREEN ----------------
        if state == "race" and e.type == pygame.KEYDOWN:
            moved = False
            key = e.key

            # Apply randomised controls if enabled
            if random_controls and key in control_map:
                key = control_map[key]

            # Player movement
            if key == pygame.K_LEFT:
                user.move(-1, 0)
                moved = True
            elif key == pygame.K_RIGHT:
                user.move(1, 0)
                moved = True
            elif key == pygame.K_UP:
                user.move(0, -1)
                moved = True
            elif key == pygame.K_DOWN:
                user.move(0, 1)
                moved = True

            # Start AI timing when player moves for first time
            if moved and not ai_started:
                ai_started = True
                start_time = time.time()

        # ---------------- MENU SCREEN ----------------
        # Handles name input if player won
        if state == "menu" and winner == "You" and not score_saved:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    # Save score and go straight to leaderboard
                    save_score(player_name if player_name else "Anonymous", total_time)
                    score_saved = True
                    state = "leaderboard"
                elif e.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 10:
                        player_name += e.unicode

        # Handle button clicks in menu
        if state == "menu" and e.type == pygame.MOUSEBUTTONDOWN:
            if leaderboard_button.check(e.pos):
                state = "leaderboard"
            elif back_button.check(e.pos):
                reset_game()
                state = "start"
                winner = None
                player_name = ""
            elif view_route_button.check(e.pos):
                state = "route_view"

        # ---------------- LEADERBOARD SCREEN ----------------
        if state == "leaderboard" and e.type == pygame.MOUSEBUTTONDOWN:
            if back_button.check(e.pos):
                state = "menu"  # Returning from leaderboard shows menu without textbox

        # ---------------- AI ROUTE VIEW ----------------
        if state == "route_view" and e.type == pygame.MOUSEBUTTONDOWN:
            if back_button.check(e.pos):
                state = "menu"


    # ------------------- DRAWING -------------------
    screen.fill((0, 0, 0))

    # --------------- START SCREEN -----------------
    if state == "start":
        screen.blit(font_big.render("Algorithm Racer", True, (255, 255, 255)), (100, 50))
        start_button.draw()
        difficulty_button.draw()

    # --------------- DIFFICULTY SCREEN -----------------
    elif state == "difficulty":
        screen.blit(font_small.render(f"Current Algorithm: {current_algorithm}", True, (255, 255, 255)), (80, 30))
        screen.blit(font_small.render(f"Maze Size: {maze_size}x{maze_size}", True, (255, 255, 255)), (240, 420))
        size5_btn.draw()
        size8_btn.draw()
        size10_btn.draw()
        size20_btn.draw()
        bfs_button.draw()
        dfs_button.draw()
        dijkstra_button.draw()
        slider.draw()
        back_button.draw()
        # Update ??? button
        if random_controls:
            random_button.text = main_font.render("??? ON", True, (255, 255, 255))
        else:
            random_button.text = main_font.render("??? OFF", True, (255, 255, 255))
        random_button.text_rect = random_button.text.get_rect(center=random_button.rect.center)
        random_button.draw()
        screen.blit(font_small.render(f"Algorithm Speed: {slider.value}", True, (255, 255, 255)), (215, 330))

    # --------------- RACE SCREEN -----------------
    elif state == "race":
        for col in maze:
            for c in col:
                c.draw()
        if ai_started:
            racer.step()
        racer.draw()
        finish.draw()
        user.draw()
        just_started = False

        # Check for win conditions
        if user.rect.colliderect(finish.rect) and winner is None and not just_started:
            total_time = time.time() - start_time
            winner = "You"
            # Menu will now show textbox for name entry
            state = "menu"
        elif racer.goal in racer.visited and winner is None:
            total_time = time.time() - start_time
            winner = current_algorithm
            state = "menu"

    # --------------- MENU SCREEN -----------------
    elif state == "menu":
        # Display winner and time
        screen.blit(font_big.render(f"{winner} Won!", True, (255, 255, 255)), (250, 200))
        screen.blit(font_small.render(f"Time: {total_time:.2f}s", True, (255, 255, 255)), (300, 260))

        # Only draw textbox if player won and hasn't submitted name
        if winner == "You" and not score_saved:
            screen.blit(font_small.render("Enter Name:", True, (255, 255, 255)), (300, 330))
            pygame.draw.rect(screen, (255, 255, 255), (300, 370, 200, 40), 2)
            screen.blit(font_small.render(player_name, True, (255, 255, 255)), (310, 375))

        # Buttons
        view_route_button.draw()
        leaderboard_button.draw()
        back_button.draw()

    # --------------- ROUTE VIEW SCREEN -----------------
    elif state == "route_view":
        for col in maze:
            for c in col:
                c.draw()
        racer.draw()
        finish.draw()
        screen.blit(font_big.render("AI Route", True, (255, 255, 255)), (300, 40))
        screen.blit(font_big.render(f"Moves: {len(racer.path)}", True, (255, 255, 255)), (300, 140))
        back_button.draw()

    # --------------- LEADERBOARD SCREEN -----------------
    elif state == "leaderboard":
        screen.blit(font_big.render(f"{maze_size}x{maze_size} Leaderboard", True, (255, 215, 0)), (160, 80))
        y = 170
        for i, (n, t) in enumerate(read_leaderboard()[:10], 1):
            screen.blit(font_small.render(f"{i}. {n} - {t:.2f}s", True, (255, 255, 255)), (200, y))
            y += 35
        back_button.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
