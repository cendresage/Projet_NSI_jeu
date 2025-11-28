import pygame 
from entity import Entity
from screen import Screen
from keylistener import Keylistener
from bullet import Bullet

class Player(Entity):

    def __init__(self, keylistener : Keylistener, screen : Screen, x: int, y: int):
        super().__init__(keylistener, screen, x, y)

        self.point = 0

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
    
    def fire(self):
        return Bullet(self.position.x, self.position.y, self.direction, 10, pygame.image.load("Sprites/Bullet/bullet.png"))
