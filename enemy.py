import pygame
import random
import math
from entity import Entity
from tool import Tool
from bullet import Bullet

class Enemy(Entity):
    def __init__(self, screen, player, x, y):
        super().__init__(None, screen, x, y)

        self.player = player
        self.spritesheet = pygame.image.load("Sprites/Personnages/Ennemie.png")
        self.image = Toole.split_image(self.spritesheet, 0, 0, 40, 40)
        self.all_image = self.get_all_images()

        #Paramètres de l'IA
        self.speed = 0,5
        self.detection_radius = 200                                                 # Rayon de detection de l'ennemi
        self.attack_radius = 150                                                    # Rayon de l'attaque
        
        #Gestion des états
        self.mode = "idle"
        self.idle_move_time = 0
        self.idle_direction = pygame.math.Vector2(0,0)

        #Gestion du tir
        self.last_shot_timer = 0
        self.shoot_cooldown = 1500

    
    def update(self):
        self.ai_behavior()
        super().update()

    def ai_behavior(self):
        dist_vector = self.player.position - self.position
        distance = dist_vector.length()

        if distance < self.detection_radius:
            self.mode = "attack"
        else:
            self.mode = "idle"

        if self.mode == "idle":
            self.wander()
        elif self.mode == "attack":
            self.chase_and_shoot(dist_vector, distance)

    
    def wander(self):
        now = pygame.time.get_ticks()

        if now - self.idle_move_timer > 2000:
            self.idle_move_timer = now

            choices = [
                pygame.math.Vector2(0,-1),
                pygame.math.Vector2(0,1),
                pygame.math.Vector2(-1,0),
                pygame.math.Vector2(1,0),
                pygame.math.Vector2(0,0)
            ]

            self.idle_direction = random.choice(choices)

        self.apply_movement(self.idle_direction)

    def chase_and_shoot(self, dist_vector, distance):
        
        if distance > 30:
            direction = dist_vector.normalize()
            self.apply_movement(direction)
        
        if distance < self.attack_radius:
            now = pygame.time.get_ticks()
            if now - self.last_shot_timer > self.shoot_cooldown:
                self.last_shot_timer = now
                self.fire_at_player(dist_vector)

    def apply_movement(self, direction):
        self.animation_walk = False                
         
        if direction.x < 0:
            self.move_left()
        elif direction.x > 0:
            self.move_right()
        elif direction.y < 0:
            self.move_up()
        elif direction.y > 0:
            self.move_down()

    def fire_at_player(self, direction_vector):
        bullet_dir = direction_vector.normalize()
        return Bullet(self.position.x, self.position.y, bullet_dir, 5, pygame.image.load("Sprites/Bullet/Enemy_bullet.png"))
        