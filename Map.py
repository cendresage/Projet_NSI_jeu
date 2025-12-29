import pygame
import pytmx
import pyscroll
import json
import os

from Screen import Screen
from Player import Player
from Switch import Switch
from Enemy import Enemy


class Map:
    def __init__(self, screen: Screen, enemy_group: pygame.sprite.Group):
        self.screen = screen
        self.enemy_group = enemy_group
        self.tmx_data = None
        self.map_layer = None
        self.group = None

        self.player: Player = None
        self.switchs: list[Switch]
        self.collision: list[pygame.Rect] | None = None

        self.map_layer_config = {
            "map0": 6,
            "map2": 8
        }

        self.spawn_data = self.load_spawn_data()

        self.current_map = Switch("switch", "map0", pygame.Rect(0, 0, 0, 0), 0)

        self.switch_map(self.current_map)

    def load_spawn_data(self):
        path = "assets/data/spawns.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        else:
            print(f"Erreur: Fichier {path} introuvable.")
            return {}


    def switch_map(self, switch: Switch):
        self.current_map_name = switch.name
        print(f"Chargement de la carte : {self.current_map_name}")
        self.tmx_data = pytmx.load_pygame(f"assets/map/{switch.name}.tmx")
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 3                                                                      # Zoom
        
        layer_index = self.map_layer_config.get(self.current_map_name, 6)
        print(f" Calque par défaut défini sur : {layer_index}")

        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=layer_index)

        self.switchs = []
        self.collisions = []
        self.water_collisions = []

        for obj in self.tmx_data.objects:
            if obj.name == "collision":
                self.collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            if obj.name == "collision1":
                self.water_collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            
            # Petite sécurité si un objet n'a pas de nom dans Tiled
            if obj.name is None: continue 
            
            type = obj.name.split(" ")[0]
            if type == "switch":
                self.switchs.append(Switch(
                    type, obj.name.split(" ")[1], pygame.Rect(obj.x, obj.y, obj.width, obj.height), int(obj.name.split(" ")[-1])
                ))

        self.spawn_enemies()

# Code à optimiser ici
        if self.player:
            self.pose_player(switch)
            self.player.align_hitbox()
            self.player.add_switchs(self.switchs)
            self.player.add_collisions(self.collisions + self.water_collisions)

            if hasattr(self.player, "_layer"):
                del self.player._layer

            self.group.add(self.player)
        
        self.current_map = switch


    def spawn_enemies(self):
        self.enemy_group.empty()

        if self.current_map_name in self.spawn_data:
            enemies_list = self.spawn_data[self.current_map_name]
            print(f"-> Spawning {len(enemies_list)} ennemis pour {self.current_map_name}")

            for enemy_info in enemies_list:
                if self.player:
                    x = enemy_info["x"]
                    y = enemy_info["y"]
                    hp = enemy_info.get("hp", 2)

                    points = enemy_info.get("points", 10)

                    new_enemy = Enemy(self.screen, self.player, x, y, max_hp=hp, points=points)
                    new_enemy.spawn_info = enemy_info
                    new_enemy.add_walls(self.collisions + self.water_collisions)
                    self.group.add(new_enemy)
                    self.enemy_group.add(new_enemy)

        print(f"-> Aucune donnée de spawn trouvée pour {self.current_map_name} dans le JSON")

    
    def remove_dead_enemy(self, enemy):
        """Supprime définitivement un ennemi des données de spawn"""
        if hasattr(enemy, "spawn_info"):
            # On récupère la liste des spawns de la carte actuelle
            spawns = self.spawn_data.get(self.current_map_name)
            
            # Si la liste existe et que l'info de cet ennemi est dedans, on la supprime
            if spawns and enemy.spawn_info in spawns:
                spawns.remove(enemy.spawn_info)
                print("Ennemi supprimé de la sauvegarde temporaire !")


    def add_player(self, player):
        self.group.add(player)
        self.player = player
        self.player.align_hitbox()
        self.player.add_switchs(self.switchs)
        self.player.add_collisions(self.collisions + self.water_collisions)
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
                continue                #On passe à la balle suivante

            if bullet.hitbox.collidelist(self.collisions) > -1:
                bullet.kill()


        self.group.center(self.player.rect.center)                                                    # Centrer le joueur
        self.group.draw(self.screen.get_display())


    def pose_player(self, switch: Switch):
        position = self.tmx_data.get_object_by_name("spawn " + self.current_map.name + " " + str(switch.port))
        self.player.position = pygame.math.Vector2(position.x + 5, position.y + 18)

