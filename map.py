import pygame
import pytmx
import pyscroll

from screen import Screen
from player import Player


class Map:
    def __init__(self, screen: Screen):
        self.screen = screen
        self.tmx_data = None
        self.map_layer = None
        self.group = None

        self.switch_map("map0")                                                                        # Chargement de la map
        self.player: Player = None

    def switch_map(self, map: str):
        self.tmx_data = pytmx.load_pygame(f"assets/map/{map}.tmx")
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 3                                                                      # Zoom
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=4)

    def add_player(self, player):
        self.group.add(player)
        self.player = player
        self.player.align_hitbox()

    def update(self, bullet_group: pygame.sprite.Group):
        self.group.update()
        screen_width, screen_height = self.screen.get_size()
        visible_rect = pygame.Rect(0,0, screen_width, screen_height)
        visible_rect.center = self.player.rect.center

        out_of_bounds_rect = visible_rect.inflate(100,100)

        for bullet in bullet_group.copy():
            if not bullet.hitbox.colliderect(out_of_bounds_rect):
                bullet.kill()
                
        self.group.center(self.player.rect.center)                                                    # Centrer le joueur
        self.group.draw(self.screen.get_display())