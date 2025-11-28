import pygame

from screen import Screen
from map import Map
from entity import Entity
from keylistener import Keylistener
from player import Player

class Game:
    def __init__(self):
        self.running = True
        self.screen = Screen()
        self.map = Map(self.screen)
        self.keylistener = Keylistener()
        self.Player = Player(self.keylistener, self.screen, 0, 0)
        self.map.add_player(self.Player)
        self.player_bullets = pygame.sprite.Group()


    def run(self):
        while self.running:
            self.handle_input()
            self.map.update(self.player_bullets)
            self.screen.update()

    def handle_input(self):
        for event in pygame.event.get():                # Gestion des évènements (récupère les touches pressées)
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                self.keylistener.add_key(event.key)
            elif event.type == pygame.KEYUP:
                self.keylistener.remove_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:                   # Bouton gauche de la souris
                    new_bullet = self.Player.fire()
                    self.player_bullets.add(new_bullet)
                    self.map.group.add(new_bullet)