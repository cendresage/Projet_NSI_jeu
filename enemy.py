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
        self.action_animation = 50
        self.patrol_center = self.position.copy()
        self.patrol_radius = 80                                                     # L'ennemi bouge dans un carré de 160x160 autour de patrol_center
        self.detection_radius = 200                                                 # Rayon de detection de l'ennemi
        self.attack_radius = 150


        #Gestion des états
        self.mode = "patrol"
        self.idle_move_time = 0
        self.idle_direction = pygame.math.Vector2(0,0)

        #Gestion du tir
        self.last_shot_timer = 0
        self.shoot_cooldown = 1000

    
    def update(self):
        bullet = self.ai_behavior()
        super().update()
        return bullet

    def ai_behavior(self):

        bullet = None
        dist_vector = self.player.position - self.position
        distance = dist_vector.length()

        if distance < self.detection_radius:
            self.mode = "attack"
        else:
            self.mode = "patrol" # Retour à la patrouille si le joueur est loin


        if self.mode == "patrol":
            self.patrol()
        elif self.mode == "attack":
            bullet = self.shoot_and_patrol(dist_vector, distance)
            
        return bullet


    def patrol(self):
        if self.animation_walk:
            return

        now = pygame.time.get_ticks()
        # Nouvelle décision de mouvement toutes les 2 secondes
        if now - self.idle_move_timer > 2000:
            self.idle_move_timer = now

            # Calcul du mouvement vers un point aléatoire dans la zone
            target_x = self.patrol_center.x + random.randint(-self.patrol_radius, self.patrol_radius)
            target_y = self.patrol_center.y + random.randint(-self.patrol_radius, self.patrol_radius)
            
            # Déterminer la direction principale pour y aller (Mouvement case par case)
            dx = target_x - self.position.x
            dy = target_y - self.position.y
            
            if abs(dx) > abs(dy):
                direction = pygame.math.Vector2(1, 0) if dx > 0 else pygame.math.Vector2(-1, 0)
            else:
                direction = pygame.math.Vector2(0, 1) if dy > 0 else pygame.math.Vector2(0, -1)
            
            self.idle_direction = direction

        self.apply_movement(self.idle_direction)
    

    def shoot_and_patrol(self, dist_vector, distance):
        
        # PRIORITÉ 1 : TIRER SI À PORTÉE
        if distance < self.attack_radius:
            now = pygame.time.get_ticks()
            if now - self.last_shot_timer > self.shoot_cooldown:
                self.last_shot_timer = now
                return self.fire_at_player(dist_vector) # Tirez immédiatement
        
        # PRIORITÉ 2 : PATROUILLER DANS LA ZONE EN ATTENDANT LE PROCHAIN TIR
        self.patrol()
        
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