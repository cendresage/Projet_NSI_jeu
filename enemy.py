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
        self.image = Tool.split_image(self.spritesheet, 0, 0, 40, 40)
        self.all_images = self.get_all_images()

        #Paramètres de l'IA
        self.action_animation = 55
        self.detection_radius = 200                                                 # Rayon de detection de l'ennemi
        self.attack_radius = 150
        self.out_of_range_radius = 300                                                    # Rayon de l'attaque
        
        #Gestion des états
        self.mode = "idle"
        self.idle_move_time = 0
        self.idle_direction = pygame.math.Vector2(0,0)

        #Gestion du tir
        self.last_shot_timer = 0
        self.shoot_cooldown = 1500

    
    def update(self):
        bullet = self.ai_behavior()
        super().update()
        return bullet

    def ai_behavior(self):

        dist_vector = self.player.position - self.position
        distance = dist_vector.length()

        if self.mode == "idle":
            if distance < self.detection_radius:
                self.mode = "attack"
        elif self.mode == "attack":
            if distance > self.out_of_range_radius: # Il faut s'éloigner plus pour le semer
                self.mode = "idle"

        if self.mode == "idle":
            self.wander()
        elif self.mode == "attack":
            return self.chase_and_shoot(dist_vector, distance)
        return None

    
    def wander(self):
        if self.animation_walk:
            return

        now = pygame.time.get_ticks()
        if now - self.idle_move_time > 2000:
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
        
        dx = abs(dist_vector.x)
        dy = abs(dist_vector.y)

        alignment_threshold = 20

        if distance < self.attack_radius:
            is_aligned_x = dy < alignment_threshold
            is_aligned_y = dx < alignment_threshold

            if is_aligned_x and is_aligned_y:
                now = pygame.time.get_ticks()
                if now - self.last_shot_timer > self.shoot_cooldown:
                    self.last_shot_timer = now
                    return self.fire_at_player(dist_vector)
            return None
        
        if self.animation_walk: return None

        direction = pygame.math.Vector2(0,0)

        if distance < 60:
            if dx > dy:
                direction.x = -1 if dist_vector.x > 0 else 1
            else:
                direction.y = -1 if dist_vector.y > 0 else 1

        else:
            if dx < dy:
                if dist_vector.x > 0:
                    direction.x = 1
                else:
                    direction.x = -1
            else:
                if dist_vector.y > 0:
                    direction.y = 1
                else:
                    direction.y = -1
        
        self.apply_movement(direction)
        return None


    def apply_movement(self, direction):
        # IMPORTANT : Si on est déjà en animation de marche (entre deux cases), on interdit de changer d'avis
        if self.animation_walk:
            return                
         
        if direction.x < 0:
            self.move_left()
        elif direction.x > 0:
            self.move_right()
        elif direction.y < 0:
            self.move_up()
        elif direction.y > 0:
            self.move_down()

    def fire_at_player(self, direction_vector):
        # Sécurité : Si le vecteur est nul (joueur sur l'ennemi), on prend une direction par défaut
        if direction_vector.length() == 0:
            bullet_dir = pygame.math.Vector2(1, 0)
        else:
            bullet_dir = direction_vector.normalize()
            
        return Bullet(self.position.x, self.position.y, bullet_dir, 5, pygame.image.load("Sprites/Bullet/Enemy_bullet.png"))