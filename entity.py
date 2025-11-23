import pygame
from tool import Tool
from keylistener import Keylistener
from screen import Screen

class Entity(pygame.sprite.Sprite):

    def __init__(self, keylistener: Keylistener, screen: Screen, x: int, y: int):
        super().__init__()
        self.keylistener = keylistener
        self.spritesheet = pygame.image.load("Sprites/Player.png")
        self.image = Tool.split_image(self.spritesheet,0, 0, 40, 40)
        self.position: pygame.math.Vector2 = pygame.math.Vector2(x + 16,y + 32)
        self.rect: pygame.Rect = self.image.get_rect()
        self.all_images = self.get_all_images()

        self.hitbox: pygame.Rect = pygame.Rect(0, 0, 16, 16)

    def update(self):
        self.rect.center = self.position
        self.hitbox.midbottom = self.rect.midbottom                                         # Mise à jour de la hitbox ( au niveau du corp de l'entité )


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


    def align_hitbox(self):
        self.rect.center = self.position
        self.hitbox.midbottom = self.rect.midbottom
        while self.hitbox.x % 16 != 0:                                           # Alignement de la hitbox ( si l'entité n'est pas sur une ligne noir )
            self.rect.x -= 1                                                     # On bouge l'entité vers la gauche
            self.hitbox.midbottom = self.rect.midbottom                          # Mise à jour de la hitbox pour terminer la boucle while
        while self.hitbox.y % 16 != 0:
            self.rect.y   -= 1
            self.hitbox.midbottom = self.rect.midbottom
        self.position = pygame.math.Vector2(self.rect.center)                     # Mise à jour de l'entité aligner sur la grille

    def get_all_images(self):
        all_images = {
            "down": [],
            "up": [],
            "left": [],
            "right": []
        }

        width: int = self.spritesheet.get_width() // 4
        height: int = self.spritesheet.get_height() // 4 

        for i in range(4):
            for j, key in enumerate(all_images.keys()):
                all_images[key].append(Tool.split_image(self.spritesheet, i * width, j * height, 40, 40))
            
        return all_images
                
