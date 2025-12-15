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

        self.switchs: list[Switch]
        self.change_map: Switch | None = None

    def update(self):
        super().update()
        self.check_move()

    def check_move(self):
        if self.animation_walk is False:
            temp_hitbox = self.hitbox.copy()
            if self.keylistener.key_pressed(pygame.K_q) or self.keylistener.key_pressed(pygame.K_LEFT):
                temp_hitbox.x -= 16
                self.check_collisions_switchs(temp_hitbox)
                self.move_left()
            elif self.keylistener.key_pressed(pygame.K_d) or self.keylistener.key_pressed(pygame.K_RIGHT):
                temp_hitbox.x += 16
                self.check_collisions_switchs(temp_hitbox)
                self.move_right()
            elif self.keylistener.key_pressed(pygame.K_z) or self.keylistener.key_pressed(pygame.K_UP):
                temp_hitbox.y -= 16
                self.check_collisions_switchs(temp_hitbox)
                self.move_up()
            elif self.keylistener.key_pressed(pygame.K_s) or self.keylistener.key_pressed(pygame.K_DOWN):
                temp_hitbox.y += 16
                self.check_collisions_switchs(temp_hitbox)
                self.move_down()
            
            

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

    def fire(self):
        direction_vector = self.get_direction_vector()

        return Bullet(self.position.x, self.position.y, direction_vector, 5, pygame.image.load("Sprites/Bullet/Player_bullet.png"))
    

    def damage(self, amount):
        if self.hp > 0:
            self.hp -= amount
            if self.hp <= 0:
                self.hp = 0
                print("Game Over")  # game over à gérer plus tard


    def add_switch(self, switch : list[Switch]):
        self.switchs = switchs 

    def check_collisions_switchs(self, temp_hitbox):
        if self.swiths:
            for switch in self.switchs:
                if switch.check_collision(self.hitbox):
                    self.change_map = switch
        return None