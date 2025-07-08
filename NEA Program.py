import pygame

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Algorithm Racer")
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
    def place(self,startx,starty):
        screen.blit(self.__image, (self.rect.x, self.rect.y))
class finish(pygame.sprite.Sprite):
    def __init__(self, image, dimentions, startx, starty):
        super().__init__()
        self.__image = pygame.image.load(image).convert_alpha()
        self.__image = pygame.transform.scale(self.__image, (dimentions,dimentions))
        self.rect = self.__image.get_rect()
        self.rect.x = startx
        self.rect.y = starty
        self.direction = "None"
        self._dimentions = dimentions
    def place(self,startx,starty):
        screen.blit(self.__image, (self.rect.x, self.rect.y))
finish = finish("apple.jpg", 100, 500, 200)
wall1 = wall("wall.jpg", 100, 0, 0)
wall2 = wall("wall.jpg", 100, 100, 0)
wall3 = wall("wall.jpg", 100, 200, 0)
wall4 = wall("wall.jpg", 100, 300, 0)
wall5 = wall("wall.jpg", 100, 400, 0)
wall6 = wall("wall.jpg", 100, 500, 0)
wall7 = wall("wall.jpg", 100, 0, 200)
wall8 = wall("wall.jpg", 100, 0, 300)
wall9 = wall("wall.jpg", 100, 0, 400)
wall10 = wall("wall.jpg", 100, 0, 500)
wall11 = wall("wall.jpg", 100, 100, 500)
wall12 = wall("wall.jpg", 100, 200, 500)
wall13 = wall("wall.jpg", 100, 300, 500)
wall14 = wall("wall.jpg", 100, 400, 500)
wall15 = wall("wall.jpg", 100, 500, 500)
wall16 = wall("wall.jpg", 100, 500, 400)
wall17 = wall("wall.jpg", 100, 500, 300)
wall18 = wall("wall.jpg", 100, 500, 100)
wall19 = wall("wall.jpg", 100, 200, 200)
wall20 = wall("wall.jpg", 100, 200, 300)
wall21 = wall("wall.jpg", 100, 400, 300)
wall22 = wall("wall.jpg", 100, 300, 0)

        
class User(pygame.sprite.Sprite):
    def __init__(self, image, width, height, startx, starty, lastx, lasty):
        super().__init__()
        self.__width = width
        self.__height = height
        self.__image = pygame.image.load(image).convert_alpha()
        self.__image = pygame.transform.scale(self.__image, (width, height))
        self.rect = self.__image.get_rect()
        self.rect.x = startx
        self.rect.y = starty
        self.rect.x = lastx
        self.rect.y = lasty
        
        self.direction = "None"

    def draw(self,startx, starty):
        screen.blit(self.__image, (self.rect.x, self.rect.y))
user = User('user.jpg', 92, 92, 100, 200,100,200)
running = True
state = "game"

while running:
    def game():
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

        user.previous_x = user.rect.x 
        user.previous_y = user.rect.y

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
        spriteGroup.add(wall2)
        spriteGroup.add(wall3)
        spriteGroup.add(wall4)
        spriteGroup.add(wall5)
        spriteGroup.add(wall6)
        spriteGroup.add(wall7)
        spriteGroup.add(wall8)
        spriteGroup.add(wall9)
        spriteGroup.add(wall10)
        spriteGroup.add(wall11)
        spriteGroup.add(wall12)
        spriteGroup.add(wall13)
        spriteGroup.add(wall14)
        spriteGroup.add(wall15)
        spriteGroup.add(wall16)
        spriteGroup.add(wall17)
        spriteGroup.add(wall18)
        spriteGroup.add(wall19)
        spriteGroup.add(wall20)
        spriteGroup.add(wall21)
        spriteGroup.add(wall22)
        

        # Collision Detection
        collisions = pygame.sprite.spritecollide(user, spriteGroup, True)
        for i in collisions:
              user.rect.x = user.previous_x
              user.rect.y = user.previous_y
        end_found =  pygame.sprite.Group()
        end_found.add(finish)

        game_done = pygame.sprite.spritecollide(user, end_found, True)
        for i in game_done:
            state = "menu"
    

        
        


        
        # Draw Image
        user.draw(100,200)
        finish.place(500,200)
        wall1.place(20,20)
        wall2.place(40,20)
        wall3.place(60,20)
        wall4.place(80,20)
        wall5.place(100,20)
        wall6.place(120,20)
        wall7.place(20,60)
        wall8.place(20,80)
        wall9.place(20,100)
        wall10.place(20,120)
        wall11.place(40,120)
        wall12.place(60,120)
        wall13.place(80,120)
        wall14.place(100,120)
        wall15.place(120,120)
        wall16.place(120,100)
        wall17.place(120,80)
        wall18.place(120,40)
        wall19.place(60,60)
        wall20.place(60,80)
        wall21.place(100,80)
        wall22.place(80,20)
        
    def menu():
        screen.fill((0,0,255))

    if state == "game":
        game()
    elif state == "menu":
        menu()

            
    
    # Update the display
    pygame.display.update()

    # 60 FPS
    clock.tick(60)
