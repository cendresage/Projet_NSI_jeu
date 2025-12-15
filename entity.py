import pygame
from tool import Tool
from keylistener import Keylistener
from screen import Screen

class Entity(pygame.sprite.Sprite):

    def __init__(self, keylistener: Keylistener, screen: Screen, x: int, y: int):
        super().__init__()
        self.screen = screen
        self.keylistener = keylistener
        self.spritesheet = pygame.image.load("Sprites/Personnages/Player.png")
        self.image = Tool.split_image(self.spritesheet,0, 0, 40, 40)
        self.position: pygame.math.Vector2 = pygame.math.Vector2(x, y)
        self.rect: pygame.Rect = self.image.get_rect()
        self.all_images = self.get_all_images()
        self.index_image = 0 
        self.image_part = 0
        self.reset_animation = False
        self.hitbox: pygame.Rect = pygame.Rect(0, 0, 25, 33)

        self.step: int = 0
        self.animation_walk: bool = False
        self.direction = "down"

        self.animation_step_time = 0.0
        self.action_animation = 18

    def update(self):
        self.animation_sprite()
        self.move()
        self.rect.center = self.position
        self.hitbox.midbottom = self.rect.midbottom                                         # Mise à jour de la hitbox ( au niveau du corp de l'entité )
        self.image = self.all_images[self.direction][self.index_image]


    def move_left(self):
        self.animation_walk = True
        self.direction = "left"

    def move_right(self):
        self.animation_walk = True
        self.direction = "right"

    def move_up(self):
        self.animation_walk = True
        self.direction = "up"

    def move_down(self):
        self.animation_walk = True
        self.direction = "down"


    def animation_sprite(self):
        if int(self.step // 8) + self.image_part >= 4:
            self.image_part = 0
            self.reset_animation = True
        self.index_image = int(self.step // 8) + self.image_part 



    def move(self):
        if self.animation_walk:
            self.animation_step_time += self.screen.get_delta_time()

            # CHANGEMENT : Utilisation d'une boucle while pour gérer les ralentissements
            # Permet de déclencher plusieurs pas (mouvements de 1 pixel) dans une seule frame 
            # si le temps écoulé (lag) le justifie.
            while self.step < 16 and self.animation_step_time >= self.action_animation:
                
                self.step += 1
                if self.direction == "left":
                    self.position.x -= 1
                elif self.direction == "right":
                    self.position.x += 1
                elif self.direction == "up":
                    self.position.y -= 1
                elif self.direction == "down":
                    self.position.y += 1
                
                # Déduit le temps écoulé pour ce pas (16 ms)
                self.animation_step_time -= self.action_animation
                
            if self.step >= 16:
                self.step = 0
                self.animation_walk = False 
                if self.reset_animation:
                    self.reset_animation = False
                else:
                    if self.image_part == 0:
                        self.image_part = 2
                    else:
                        self.image_part = 0


    def align_hitbox(self):
        self.position.x += 15
        self.position.y += 32
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
                
