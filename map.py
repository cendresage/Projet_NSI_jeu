import pygame
import pytmx
import pyscroll
import json
import os

from screen import Screen
from player import Player
from switch import Switch
from enemy import Enemy


class Map:
    def __init__(self, screen: Screen, enemy_group: pygame.sprite.Group):
        self.screen = screen
        self.enemy_group = enemy_group
        self.tmx_data = None
        self.map_layer = None
        self.group = None

        self.player: Player = None
        self.switchs: list[Switch]

        self.spawn_data = self.load_spawn_data()

        self.current_map = Switch("switch", "map0", pygame.Rect(0, 0, 0, 0), 0)

        self.switch_map(self.current_map)

    def load_spawn_data(self):
        path = "assets/map/spawns.txt"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        else:
            print("Erreur: Fichier spawns.json introuvable.")
            return {}


    def switch_map(self, switch: Switch):
        self.current_map_name = switch.name
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

        self.spawn_enemies()

        if self.player:
            self.pose_player(switch)
            self.player.align_hitbox()
            self.player.add_switchs(self.switchs)
            self.group.add(self.player)
        
        self.current_map = switch


    def spawn_enemies(self):
        self.enemy_group.empty()

        if self.current_map_name in self.spawn_data:
            enemies_list = self.spawn_data[self.current_map_name]

            for enemy_info in enemies_list:
                if self.player:
                    x = enemy_info["x"]
                    y = enemy_info["y"]
                    hp = enemy_info.get("hp", 2)

                    new_enemy = Enemy(self.screen, self.player, x, y, max_hp=hp)
                    self.group.add(new_enemy)
                    self.enemy_group.add(new_enemy)


    def add_player(self, player):
        self.group.add(player)
        self.player = player
        self.player.align_hitbox()
        self.player.add_switchs(self.switchs)
        self.spawn_enemies()

    def update(self, bullet_group: pygame.sprite.Group):
        if self.player:
            if self.player.change_map:
                self.switch_map(self.player.change_map)
                self.player.change_map = None
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


    def pose_player(self, switch: Switch):
        position = self.tmx_data.get_object_by_name("spawn " + self.current_map.name + " " + str(switch.port))
        self.player.position = pygame.math.Vector2(position.x, position.y)