import pygame
import random
import sys
import time
import heapq

class AlgorithmRacer:
    def __init__(self, algo):
        self.algo = algo
        self.start = maze[0][0]
        self.goal = maze[columns-1][rows-1]
        self.visited = set()
        self.prev = {}
        self.path = []
        self.frame = 0
        self.current = self.start
        
        self.dead_ends = set()
        if algo == "Dijkstra":
            self.frontier = []
            heapq.heappush(self.frontier, (0, 0,self.start))
            self.dist = {self.start: 0}
            self.counter = 0
        else:
            self.frontier = [self.start]
    def reconstruct_path(self, target = None):
        self.path = []
        if target is not None:
            c = target
        else:
            c = self.goal
        while c in self.prev:
            self.path.append(c)
            c = self.prev[c]
        self.path.append(self.start)
        self.path.reverse()
        
    def step(self):
        self.frame += 1
        if self.frame < delay or not self.frontier:
            return
        self.frame = 0

        if self.algo == "DFS":
            current = self.frontier.pop()
        elif self.algo == "BFS":
            current = self.frontier.pop(0)
        else:
            _, _, current = heapq.heappop(self.frontier)
        self.current = current
        if current in self.visited:
            return

        self.visited.add(current)

        if current == self.goal:
            self.reconstruct_path(self.goal)
            return
        else:
            self.reconstruct_path(self.current)

        expanded = False

        for n in get_neighbors(current):
            if self.algo == "Dijkstra":
                new_d = self.dist[current] + 1
                if n not in self.dist or new_d < self.dist[n]:
                    self.dist[n] = new_d
                    self.counter += 1
                    heapq.heappush(self.frontier, (new_d, self.counter, n))
                    self.prev[n] = current
                    expanded = True
            else:
                if n not in self.visited and n not in self.frontier:
                    self.frontier.append(n)
                    self.prev[n] = current
                    expanded = True

        if not expanded and current != self.goal:
            self.dead_ends.add(current)
    
    def draw(self):
    # explored cells
        for c in self.visited:
            if c in self.dead_ends:
                colour = (130, 130, 130)
            else:
                colour = (0, 0, 150)
                
            pygame.draw.rect(screen,colour,(c.x * CELL_SIZE + 10,c.y * CELL_SIZE + 10,CELL_SIZE - 20,CELL_SIZE - 20))

        # final path dots + direction lines
        for i in range(len(self.path) - 1):
            c1 = self.path[i]
            c2 = self.path[i + 1]

            # centre of current cell
            x1 = c1.x * CELL_SIZE + CELL_SIZE // 2
            y1 = c1.y * CELL_SIZE + CELL_SIZE // 2

            # centre of next cell
            x2 = c2.x * CELL_SIZE + CELL_SIZE // 2
            y2 = c2.y * CELL_SIZE + CELL_SIZE // 2

            # draw dot
            pygame.draw.circle(screen, (255, 0, 0), (x1, y1), 5)

            # draw direction line
            pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 3)

        # draw dot on goal
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
            if abs(e.pos[0] - self.handle_x) < 12:
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

class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.visited = False
        self.walls = [True, True, True, True]

    def draw(self):
        px, py = self.x*CELL_SIZE, self.y*CELL_SIZE
        if self.walls[0]: pygame.draw.line(screen,(255,255,255),(px,py),(px+CELL_SIZE,py),2)
        if self.walls[1]: pygame.draw.line(screen,(255,255,255),(px+CELL_SIZE,py),(px+CELL_SIZE,py+CELL_SIZE),2)
        if self.walls[2]: pygame.draw.line(screen,(255,255,255),(px+CELL_SIZE,py+CELL_SIZE),(px,py+CELL_SIZE),2)
        if self.walls[3]: pygame.draw.line(screen,(255,255,255),(px,py+CELL_SIZE),(px,py),2)

class User:
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("images/user.jpg").convert_alpha(),(CELL_SIZE-8, CELL_SIZE-8))
        self.x = 0
        self.y = 0
        self.update()

    def update(self):
        self.rect = self.image.get_rect(topleft=(self.x*CELL_SIZE+4, self.y*CELL_SIZE+4))

    def move(self, dx, dy):
        cell = maze[self.x][self.y]
        if dx == -1 and not cell.walls[3]: self.x -= 1
        if dx == 1 and not cell.walls[1]: self.x += 1
        if dy == -1 and not cell.walls[0]: self.y -= 1
        if dy == 1 and not cell.walls[2]: self.y += 1
        self.update()

    def draw(self):
        screen.blit(self.image, self.rect)

class Finish:
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("images/apple.jpg").convert_alpha(),(CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect(topleft=((columns-1)*CELL_SIZE,(rows-1)*CELL_SIZE))

    def draw(self):
        screen.blit(self.image, self.rect)
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
    c = maze[0][0]
    c.visited = True
    stack.append(c)
    while stack:
        c = stack[-1]
        n = []
        for dx,dy,w,ow in [(-1,0,3,1),(1,0,1,3),(0,-1,0,2),(0,1,2,0)]:
            nx, ny = c.x+dx, c.y+dy
            if 0 <= nx < columns and 0 <= ny < rows and not maze[nx][ny].visited:
                n.append((maze[nx][ny], w, ow))
        if n:
            nxt,w,ow = random.choice(n)
            c.walls[w] = False
            nxt.walls[ow] = False
            nxt.visited = True
            stack.append(nxt)
        else:
            stack.pop()


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
    global maze, user, finish, racer, winner, start_time, ai_started, score_saved

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





def get_neighbors(cell):
    out = []
    for dx,dy,w,ow in [(-1,0,3,1),(1,0,1,3),(0,-1,0,2),(0,1,2,0)]:
        nx, ny = cell.x+dx, cell.y+dy
        if 0 <= nx < columns and 0 <= ny < rows:
            if not cell.walls[w]:
                out.append(maze[nx][ny])
    return out


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

back_button = Button(btn,400,650,"BACK")
leaderboard_button = Button(btn,400,560,"LEADERBOARD")
view_route_button = Button(btn, 400, 460, "VIEW AI ROUTE")

slider = Slider(250,380,300,1,60,30)

racer = None

# ---------------- MAIN LOOP ----------------

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if state == "start" and e.type == pygame.MOUSEBUTTONDOWN:
            if difficulty_button.check(e.pos):
                state = "difficulty"
            elif start_button.check(e.pos) and difficulty_selected and algorithm_selected:
                racer = AlgorithmRacer(current_algorithm)
                start_time = time.time()
                just_started = True
                state = "race"
                ai_started = False
                score_saved = False

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

        if state == "race" and e.type == pygame.KEYDOWN:
            moved = False
            if e.key == pygame.K_LEFT:
                user.move(-1,0)
                moved = True
            if e.key == pygame.K_RIGHT:
                user.move(1,0)
                moved = True
            if e.key == pygame.K_UP:
                user.move(0,-1)
                moved = True
            if e.key == pygame.K_DOWN:
                user.move(0,1)
                moved = True
            if moved and not ai_started:
                ai_started = True
                start_time = time.time()

        if state == "menu" and e.type == pygame.KEYDOWN and not name_submitted:
            if e.key == pygame.K_RETURN and not score_saved:
                save_score(player_name if player_name else "Anonymous", total_time)
                name_submitted = True
                score_saved = True
                
            elif e.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            else:
                if len(player_name) < 10:
                    player_name += e.unicode

        if state == "menu" and e.type == pygame.MOUSEBUTTONDOWN:
            if leaderboard_button.check(e.pos):
                state = "leaderboard"
                name_submitted = False
                player_name = ""
            elif back_button.check(e.pos):
                reset_game()
                state = "start"
                name_submitted = False
                player_name = ""
                winner = None
            elif view_route_button.check(e.pos):
                state = "route_view"

        if state == "leaderboard" and e.type == pygame.MOUSEBUTTONDOWN:
            if back_button.check(e.pos):
                state = "menu"
        if state == "route_view" and e.type == pygame.MOUSEBUTTONDOWN:
            if back_button.check(e.pos):
                state = "menu"
    screen.fill((0,0,0))

    if state == "start":
        screen.blit(font_big.render(f"Algorithm Racer",True,(255,255,255)),(100,50))
        start_button.draw()
        difficulty_button.draw()

    elif state == "difficulty":
        screen.blit(font_small.render(f"Current Algorithm Selected: {current_algorithm}",True,(255,255,255)),(80,30))
        screen.blit(font_small.render(f"Maze Size: {maze_size}x{maze_size}", True, (255,255,255)), (240, 420))
        size5_btn.draw()
        size8_btn.draw()
        size10_btn.draw()
        size20_btn.draw()
        bfs_button.draw()
        dfs_button.draw()
        dijkstra_button.draw()
        slider.draw()
        back_button.draw()
        screen.blit(font_small.render(f"Algorithm Speed: {slider.value}",True,(255,255,255)),(215,330))

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

        if user.rect.colliderect(finish.rect) and winner is None and not just_started:
            total_time = time.time() - start_time
            winner = "You"
            state = "menu"
        elif racer.goal in racer.visited:
            total_time = time.time() - start_time
            winner = current_algorithm
            state = "menu"

    elif state == "menu":
        screen.blit(font_big.render(f"{winner} Won!",True,(255,255,255)),(250,200))
        screen.blit(font_small.render(f"Time: {total_time:.2f}s",True,(255,255,255)),(300,260))
        if winner == "You":
            screen.blit(font_small.render("Enter Name:",True,(255,255,255)),(300,330))
            pygame.draw.rect(screen,(255,255,255),(300,370,200,40),2)
        screen.blit(font_small.render(player_name,True,(255,255,255)),(310,375))
        view_route_button.draw()
        leaderboard_button.draw()
        back_button.draw()
    elif state == "route_view":
        screen.fill((0,0,0))

        for col in maze:
            for c in col:
                c.draw()

        racer.draw()
        finish.draw()

        screen.blit(font_big.render("AI Route", True, (255,255,255)),(300, 40))
        screen.blit(font_big.render(f"Moves: {len(racer.path)}", True, (255,255,255)),(300, 140))

        back_button.draw()

    elif state == "leaderboard":
        screen.blit(font_big.render(f"{maze_size}x{maze_size} Leaderboard",True,(255,215,0)),(160,80))
        y = 170
        for i,(n,t) in enumerate(read_leaderboard()[:10],1):
            screen.blit(font_small.render(f"{i}. {n} - {t:.2f}s",True,(255,255,255)),(200,y))
            y += 35
        back_button.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
