import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Game Title")
clock = pygame.time.Clock()

class wall(pygame.sprite.Sprite):
    def __init__(self, image,dimentions, startx, starty):
        super().__init__()
        self.__image = pygame.image.load(image).convert_alpha()
        self.__image = pygame.transform.scale(self.__image, (dimentions,dimentions))
        self.rect = self.__image.get_rect()
        self.rect.x = startx
        self.rect.y = starty
        self.direction = "None"
        self._dimentions = dimentions
    def collision(self):
        print("Collision")
    def place(self,startx,starty):
        screen.blit(self.__image, (self.rect.x, self.rect.y))
wall1 = wall("wall.jpg", 25, 20, 20)
wall1.place(20,20)
        
class User(pygame.sprite.Sprite):
    def __init__(self, image, width, height, startx, starty):
        super().__init__()
        self.__width = width
        self.__height = height
        self.__image = pygame.image.load(image).convert_alpha()
        self.__image = pygame.transform.scale(self.__image, (width, height))
        self.rect = self.__image.get_rect()
        self.rect.x = startx
        self.rect.y = starty
        self.direction = "None"

    def draw(self):
        screen.blit(self.__image, (self.rect.x, self.rect.y))
user = User('user.jpg', 20, 20, 0, 0)
running = True
while running:
    
    # Draw the background
    screen.fill((100,0,255)) 

    # Get all of the user actions and inputs
    for event in pygame.event.get():
        # If they click the cross to close the window
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
    
        # Movement key presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                user.direction = "Left"
            elif event.key == pygame.K_RIGHT:
                user.direction = "Right"
            elif event.key == pygame.K_UP:
                user.direction = "Up"
            elif event.key == pygame.K_DOWN:
                user.direction = "Down"
                
        if event.type == pygame.KEYUP:
            user.direction = "None"

    # Player Movement
    if user.direction == "Left":
        user.rect.x -= 3
        
    if user.direction == "Right":
        user.rect.x += 3
        
    if user.direction == "Up":
        user.rect.y -= 3
        
    if user.direction == "Down":
        user.rect.y += 3
        
    spriteGroup = pygame.sprite.Group()
    spriteGroup.add(wall1)

    # Collision Detection
    collisions = pygame.sprite.spritecollide(user, spriteGroup, True)
    for i in collisions:
          self.rect.x = self.previous_x
          self.rect.y = self.previous_y
        
    # Draw shapes on the screen
    pygame.draw.rect(screen, (0,200,100), (400,300,200,100)) 
    pygame.draw.circle(screen, (235,100,25), (50,300), 20)
    pygame.draw.ellipse(screen, (20,100,200), (100,100,100,30))
    
    # Draw some text on the screen
    font = pygame.font.SysFont('Wingdings', 25)
    text = font.render("This is:",False,(0,0,0))
    screen.blit(text,(400,400))


    
    # Draw Image
    user.draw()
    wall1.place(20,20)
    
    # Update the display
    pygame.display.update()

    # 60 FPS
    clock.tick(20)
