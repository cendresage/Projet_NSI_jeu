import pygame 
from entity import Entity
from screen import Screen
from keylistener import Keylistener
from bullet import Bullet
from switch import Switch

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

    def update(self):
        self.check_input()
        super().update()
        self.check_collision_switchs
        self.check_attack_state()


    def check_attack_state(self):
        """Vérifie si le temps d'arrêt après le tir est écoulé"""
        if self.attacking:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time > self.attack_stop_duration:
                self.attacking = False
            

    def check_input(self):
        if self.animation_walk is False and not self.attacking:
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
                    if dx < 0:
                        self.move_left()
                    elif dx > 0:
                        self.move_right()
                    if dy < 0:
                        self.move_up()
                    elif dy > 0:
                        self.move_down()

    
    def check_collision_switchs(self):
        for switch in self.switchs:
            if self.hitbox.colliderect(switch.rect):
                self.change_map = switch
            
            

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
        """Tire vers la souris, oriente le joueur et l'immobilise brièvement"""
        delta_x = mouse_x - self.rect.centerx
        delta_y = mouse_y - self.rect.centery


        # Déterminer l'orientation (Haut, Bas, Gauche, Droite)

        if abs(delta_x) > abs(delta_y):
            # Mouvement horizontal dominant
            if delta_x > 0: self.direction = "right"
            else: self.direction = "left"
        else:
            # Mouvement vertical dominant
            if delta_y > 0: self.direction = "down"
            else: self.direction = "up"

        # Mettre à jour l'image tout de suite pour faire face à la souris

        self.image = self.all_images[self.direction][self.index_image]

        # Activer l'immobilisation
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()
        self.animation_walk = False


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
