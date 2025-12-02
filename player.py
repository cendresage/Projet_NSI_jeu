import pygame 
from entity import Entity
from screen import Screen
from keylistener import Keylistener
from bullet import Bullet

class Player(Entity):

    def __init__(self, keylistener : Keylistener, screen : Screen, x: int, y: int):
        super().__init__(keylistener, screen, x, y)

        self.point = 0
        self.hp = 3
        self.max_hp = 3

    def update(self):
        super().update()
        self.check_move()

    def check_move(self):
        if self.animation_walk is False:
            if self.keylistener.key_pressed(pygame.K_q) or self.keylistener.key_pressed(pygame.K_LEFT):
                self.move_left()
            if self.keylistener.key_pressed(pygame.K_d) or self.keylistener.key_pressed(pygame.K_RIGHT):
                self.move_right()
            if self.keylistener.key_pressed(pygame.K_z) or self.keylistener.key_pressed(pygame.K_UP):
                self.move_up()
            if self.keylistener.key_pressed(pygame.K_s) or self.keylistener.key_pressed(pygame.K_DOWN):
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
