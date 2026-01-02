import pygame

from Entity import Entity
from Screen import Screen
from Keylistener import Keylistener
from Bullet import Bullet
from Switch import Switch

class Player(Entity):

    def __init__(self, keylistener : Keylistener, screen : Screen, x: int, y: int):
        super().__init__(keylistener, screen, x, y)

        self.point = 0
        self.hp = 3
        self.max_hp = 3

        self.switchs: list[Switch] | None = None
        self.collisions: list[pygame.Rect] | None = None
        self.change_map: Switch | None = None

        #___----- Nouveau systeme de combat -----___
        self.attacking = False            # Est-ce que le joueur est en train de tirer ?
        self.attack_time = 0              # Quand le joueur à tirer ?
        self.attack_stop_duration = 200   # Temps d'immobilisation en ms
        self.pending_shot = None          # Stocke le tir en attente

        self.in_cutscene = False

        try:
            self.footstep_sound = pygame.mixer.Sound("musique/son_ingame/footstep.wav")
            self.footstep_sound.set_volume(0.3)
        except Exception as e:
            print(f"Erreur son pas: {e}")
            self.footstep_sound = None
        self.step_timer = 0
        self.step_interval = 350

    def update(self):
        super().update()
        if self.animation_walk:
            current_time = pygame.time.get_ticks()
            
      
            if current_time - self.step_timer > self.step_interval:
                if self.footstep_sound:
                    self.footstep_sound.play()
                
                
                self.step_timer = current_time

        self.check_input()
        self.check_collision_switchs()
        self.check_attack_state()

    def check_attack_state(self):
        """Vérifie si le temps d'arrêt après le tir est écoulé"""
        if self.attacking:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time > self.attack_stop_duration:
                self.attacking = False
                self.align_hitbox()
            

    def check_input(self):

        if self.in_cutscene:
            return

        if self.attacking:
            return

        if self.pending_shot is not None:
            return 

        
        if self.animation_walk is False:
            dx, dy = 0, 0
            if self.keylistener.key_pressed(pygame.K_q) or self.keylistener.key_pressed(pygame.K_LEFT):
                dx = -16
                self.direction = "left"
            elif self.keylistener.key_pressed(pygame.K_d) or self.keylistener.key_pressed(pygame.K_RIGHT):
                dx = 16
                self.direction = "right"
            elif self.keylistener.key_pressed(pygame.K_z) or self.keylistener.key_pressed(pygame.K_UP):
                dy = -16
                self.direction = "up"
            elif self.keylistener.key_pressed(pygame.K_s) or self.keylistener.key_pressed(pygame.K_DOWN):
                dy = 16
                self.direction = "down"   

            if dx != 0 or dy != 0:
                 future_hitbox = self.hitbox.copy()
                 future_hitbox.x += dx
                 future_hitbox.y += dy
                 if future_hitbox.collidelist(self.collisions) == -1:
                    if dx < 0: self.move_left()
                    elif dx > 0: self.move_right()
                    elif dy < 0: self.move_up()
                    elif dy > 0: self.move_down()

    
    def check_collision_switchs(self):
        # On vérifie que la liste existe pour éviter un crash si elle est None
        if self.switchs: 
            for switch in self.switchs:
                if self.hitbox.colliderect(switch.hitbox):
                    self.change_map = switch

    def check_pending_fire(self):
        """Appelé par le jeu pour vérifier si un tir doit partir maintenant"""
        if not self.animation_walk and self.pending_shot:
            target_x, target_y = self.pending_shot
            self.pending_shot = None
            return self._launch_bullet(target_x, target_y)
        return None
            
            

    def get_position(self):
        return self.position.x, self.position.y
    
    def get_direction_vector(self):
        if self.direction == "up":
            return pygame.math.Vector2(0, -1)
        elif self.direction == "down":
            return pygame.math.Vector2(0, 1)
        elif self.direction == "left":
            return pygame.math.Vector2(-1, 0)
        elif self.direction == "right":
            return pygame.math.Vector2(1, 0)

        return pygame.math.Vector2(0,0)  # pour éviter les erreurs de position

    def fire(self, mouse_x, mouse_y):
        """Gère le moment où la balle serra tirée"""

        if self.animation_walk:
            self.pending_shot = (mouse_x, mouse_y)
            return None
        return self._launch_bullet(mouse_x, mouse_y)
    
    def _launch_bullet(self, mouse_x, mouse_y):
        """Fonction pour créer la balle et figer le joueur"""
        delta_x = mouse_x - self.rect.centerx
        delta_y = mouse_y - self.rect.centery

        if abs(delta_x) > abs(delta_y):
            self.direction = "right" if delta_x > 0 else "left"
        else:
            self.direction = "down" if delta_y > 0 else "up"

        self.image = self.all_images[self.direction][self.index_image]
        
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()

        direction_vector = self.get_direction_vector()
        return Bullet(self.position.x, self.position.y, direction_vector, 5, pygame.image.load("Sprites/Bullet/Player_bullet.png"))
    

    def damage(self, amount):
        if self.hp > 0:
            self.hp -= amount
            if self.hp <= 0:
                self.hp = 0
                print("Game Over")  # game over à gérer plus tard


    
    
    def add_switchs(self, switch : list[Switch]):
        self.switchs = switch


    def add_collisions(self, collisions):
            self.collisions = collisions
