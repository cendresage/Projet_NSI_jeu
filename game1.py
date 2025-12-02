import pygame

from screen import Screen
from map import Map
from entity import Entity
from keylistener import Keylistener
from player import Player
from enemy import Enemy

class Game:
    def __init__(self):
        self.running = True
        self.screen = Screen()
        self.map = Map(self.screen)
        self.keylistener = Keylistener()
        self.Player = Player(self.keylistener, self.screen, 0, 0)
        self.map.add_player(self.Player)
        self.player_bullets = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 30)
        self.small_font = pygame.font.SysFont("Arial", 20)


        # Temporaire 
        self.ennemi1 = Enemy(self.screen, self.Player, 200, 200)
        self.map.group.add(self.ennemi1)
        self.enemy_group.add(self.ennemi1)



    def run(self):
        while self.running:
            self.handle_input()

            for enemy in self.enemy_group:
                new_bullet = enemy.update()
                if new_bullet:
                    self.map.group.add(new_bullet)
                    self.enemy_bullets.add(new_bullet)

            all_bullets = self.player_bullets.copy()
            all_bullets.add(self.enemy_bullets)

            self.map.update(all_bullets)

            self.draw_hud()

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


    def draw_hud(self):
        display = self.screen.get_display()
        
        # Affichage du score
        score_text = self.font.render(f"Points: {self.Player.point}", True, (255, 255, 255))
        display.blit(score_text, (20, 40))

        # Affichage de la vie
        MAX_HP = 100
        current_hp = 100

        hp_bar_width = 150
        hp_bar_height = 20

        pygame.draw.rect(display, (50, 50, 50), (20, 10, hp_bar_width, hp_bar_height))

        current_width = int((current_hp / MAX_HP) * hp_bar_width)
        pygame.draw.rect(display, (0, 255, 0), (20, 10, current_width, hp_bar_height))

        hp_text = self.font.render(f"HP: {current_hp}/{MAX_HP}", True, (255, 255, 255))
        display.blit(hp_text,(20 + hp_bar_width + 10, 10))