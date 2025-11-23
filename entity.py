import pygame
from tool import Tool
from keylistener import Keylistener

class Entity(pygame.sprite.Sprite):

    def __init__(self, keylistener: Keylistener):
        super().__init__()
        self.keylistener = keylistener
        self.spritesheet = pygame.image.load("Sprites/Player.png")
        self.image = Tool.split_image(self.spritesheet,0, 0, 40, 40)
        self.position = [0, 0]
        self.rect: pygame.Rect = pygame.Rect(0, 0, 40, 40)
        self.all_images = self.get_all_images()

    def update(self):
        self.check_move()
        self.rect.topleft = self.position

    def check_move(self):
        if self.keylistener.key_pressed(pygame.K_q) or self.keylistener.key_pressed(pygame.K_LEFT):
            self.move_left()
        if self.keylistener.key_pressed(pygame.K_d) or self.keylistener.key_pressed(pygame.K_RIGHT):
            self.move_right()
        if self.keylistener.key_pressed(pygame.K_z) or self.keylistener.key_pressed(pygame.K_UP):
            self.move_up()
        if self.keylistener.key_pressed(pygame.K_s) or self.keylistener.key_pressed(pygame.K_DOWN):
            self.move_down()

    def move_left(self):
        self.position[0] -= 1
        self.image = self.all_images["left"][0]

    def move_right(self):
        self.position[0] += 1
        self.image = self.all_images["right"][0]

    def move_up(self):
        self.position[1] -= 1
        self.image = self.all_images["up"][0]

    def move_down(self):
        self.position[1] += 1
        self.image = self.all_images["down"][0]


    def get_all_images(self):
        all_images = {
            "down": [],
            "up": [],
            "left": [],
            "right": []
        }
        for i in range(4):
            for j, key in enumerate(all_images.keys()):
                all_images[key].append(Tool.split_image(self.spritesheet, i*40, j*40, 40, 40))
            
        return all_images
                
