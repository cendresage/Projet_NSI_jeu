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
        self.walls: list[pygame.Rect] = [] 

        self.map_layer_config = {
            "map0": 6,
            "map1": 6,
            "map2": 7
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
            return {}

    def switch_map(self, switch: Switch):
        print(f"--- CHARGEMENT DE LA CARTE : {switch.name} ---") # DEBUG
        self.current_map_name = switch.name
        self.tmx_data = pytmx.load_pygame(f"assets/map/{switch.name}.tmx")
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 3
        
        layer_index = self.map_layer_config.get(self.current_map_name, 6)
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=layer_index)

        self.switchs = []
        self.walls = [] 

        # --- CHARGEMENT OBJETS ---
        for obj in self.tmx_data.objects:
            if obj.name is None: continue 
            
            # .strip() enlève les espaces accidentels avant/après
            # .lower() met tout en minuscule pour éviter les erreurs "Switch" vs "switch"
            name_parts = obj.name.strip().split(" ")
            type_obj = name_parts[0].lower()
            
            if type_obj == "switch":
                try:
                    target_map = name_parts[1]
                    target_port = int(name_parts[-1])
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    
                    new_switch = Switch(type_obj, target_map, rect, target_port)
                    self.switchs.append(new_switch)
                    print(f"✅ SWITCH TROUVÉ : Vers {target_map} (Port {target_port}) à la position {rect}") # DEBUG
                except Exception as e:
                    print(f"❌ ERREUR SUR UN SWITCH '{obj.name}' : {e}")

            elif type_obj == "collision": 
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # --- CHARGEMENT TUILES SOLIDES ---
        try:
            collision_layer = self.tmx_data.get_layer_by_name("collisions")
            if collision_layer:
                for x, y, image in collision_layer.tiles():
                    rect = pygame.Rect(x * 16, y * 16, 16, 16)
                    self.walls.append(rect)
        except ValueError:
            print("⚠️ Pas de calque 'collisions' trouvé (ce n'est pas grave si vous utilisez des objets)")

        print(f"TOTAL SWITCHS : {len(self.switchs)}")
        print(f"TOTAL MURS : {len(self.walls)}")
        
        self.spawn_enemies()

        if self.player:
            self.pose_player(switch)
            self.player.align_hitbox()
            self.player.add_switchs(self.switchs)
            self.player.add_walls(self.walls)
            
            if hasattr(self.player, '_layer'):
                del self.player._layer
            
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
                    points = enemy_info.get("points", 10)
                    new_enemy = Enemy(self.screen, self.player, x, y, max_hp=hp, points=points)
                    self.group.add(new_enemy)
                    self.enemy_group.add(new_enemy)

    def add_player(self, player):
        self.group.add(player)
        self.player = player
        self.player.align_hitbox()
        self.player.add_switchs(self.switchs)
        self.player.add_walls(self.walls)
        self.spawn_enemies()

    def update(self, bullet_group: pygame.sprite.Group):
        if self.player:
            if self.player.change_map:
                self.switch_map(self.player.change_map)
                self.player.change_map = None
        self.group.update()
        
        self.group.center(self.player.rect.center)
        self.group.draw(self.screen.get_display())

        screen_width, screen_height = self.screen.get_size()
        visible_rect = pygame.Rect(0,0, screen_width, screen_height)
        visible_rect.center = self.player.rect.center
        out_of_bounds_rect = visible_rect.inflate(100,100)

        for bullet in bullet_group.copy():
            if not bullet.hitbox.colliderect(out_of_bounds_rect):
                bullet.kill()
                continue
            if bullet.hitbox.collidelist(self.walls) > -1:
                bullet.kill()

    def pose_player(self, switch: Switch):
        position = self.tmx_data.get_object_by_name("spawn " + self.current_map.name + " " + str(switch.port))
        self.player.position = pygame.math.Vector2(position.x, position.y)