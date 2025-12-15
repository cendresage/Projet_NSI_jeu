import pygame
import pytmx
import pyscroll

from screen import Screen
from player import Player
from switch import Switch


class Map:
    def __init__(self, screen: Screen):
        self.screen = screen
        self.tmx_data = None
        self.map_layer = None
        self.group = None

        self.player: Player = None
        self.switchs: list[Switch]

        self.current_map = Switch("switch", "map0", pygame.Rect(0, 0, 0, 0), 0)

        self.switch_map(self.current_map)


    def switch_map(self, switch: Switch):
        self.tmx_data = pytmx.load_pygame(f"assets/map/{switch.name}.tmx")
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 3                                                                      # Zoom
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=6)

        self.switchs = []

        for obj in self.tmx_data.objects:
            type = obj.name.split(" ")[0]
            if type == "switch":
                self.switchs.append(Switch(
                    type, obj.name.split(" ")[1], pygame.Rect(obj.x, obj.y, obj.width, obj.height), int(obj.name.split(" ")[-1])
                ))


    def add_player(self, player):
        self.group.add(player)
        self.player = player
        self.player.align_hitbox()
        self.player.add_switchs(self.switchs)

    def update(self, bullet_group: pygame.sprite.Group):
        if self.player:
            if self.player.change_map:
                self.switch_map(self.player.change_map)
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