import pygame
import pytmx
import pyscroll
import json
import os

from Screen import Screen
from Player import Player
from Switch import Switch
from Enemy import Enemy
from Boss import Agis


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
        self.chests: list[pygame.Rect] = []


        self.map_layer_config = {
            "map0": 6,
            "map2": 8
        }

        self.spawn_data = self.load_spawn_data()

        self.current_map = Switch("switch", "map0", pygame.Rect(0, 0, 0, 0), 0)

        self.switch_map(self.current_map)

        # Variables pour la cutscene du boss
        self.boss_cutscene_state = 0  # 0 = Rien, 1 = Marche, 2 = Switch, 3 = Dezoom
        self.cutscene_target_y = 0

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
        self.chests = []

        for obj in self.tmx_data.objects:
            if obj.name == "collision":
                self.collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "collision1":
                self.water_collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            
            elif obj.name == "collision2":
                self.chests.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            # Petite sécurité si un objet n'a pas de nom dans Tiled
            if obj.name is None: continue 
            
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
            self.player.add_collisions(self.collisions + self.water_collisions + self.chests)

            if hasattr(self.player, "_layer"):
                del self.player._layer

            self.group.add(self.player)
        
        self.current_map = switch

        # Détection de l'entrée dans la map du boss
        if self.current_map_name == "map_boss_0":
            print("Début de la cinématique du Boss")
            self.start_boss_cutscene()


    def spawn_enemies(self):
        self.enemy_group.empty()

        if self.current_map_name == "map_boss_1":
            print("ATTENTION : Le Boss Agis apparaît !")
            boss = Agis(self.screen, self.player, 208, 144)
            self.group.add(boss)
            self.enemy_group.add(boss)

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
        self.player.add_collisions(self.collisions + self.water_collisions + self.chests)
        self.spawn_enemies()

    def update(self, bullet_group: pygame.sprite.Group):
        if self.player:
            if self.player.change_map:
                self.switch_map(self.player.change_map)
                self.player.change_map = None
        self.group.update()

        if self.boss_cutscene_state == 1:
            self.player.move_down()

            # Si on atteint la cible (les 5 blocs)
            if self.player.position.y >= self.cutscene_target_y:
                self.player.animation_walk = False
                self.boss_cutscene_state = 2 # étape suivante

        elif self.boss_cutscene_state == 2: # Switch et son
            fake_switch = Switch("switch", "map_boss_1", pygame.Rect(0, 0, 0, 0), 0)
            # On charge la nouvelle map
            self.load_boss_arena()
            try:
                slam_sound = pygame.mixer.Sound("musique/son_ingame/slam_door.wav")
                slam_sound.play()

            except:
                print("Son de porte introuvable")
            
            self.boss_cutscene_state = 3 # On passe au Dezoom
        
        elif self.boss_cutscene_state == 3: 
            if self.map_layer.zoom > 2.0:
                self.map_layer.zoom -= 0.02     # Vitesse de Dezoom
            else:
                self.map_layer.zoom = 2.0

                self.player.in_cutscene = False
                self.boss_cutscene_state = 0

                try:
                    roar_sound = pygame.mixer.Sound("musique/son_ingame/roar.wav")
                    roar_sound.set_volume(0.8)
                    roar_sound.play()

                except Exception as e:
                    print(f"Erreur chargement cri du boss : {e}")
                
                try:
                    pygame.mixer.music.load("musique/bossbattle.mp3")
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)

                except Exception as e:
                    print(f"Musique de boss introuvable : {e}")


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


    def start_boss_cutscene(self):
        # On coupe la musique et on bloque le joueur
        pygame.mixer.music.stop()
        self.player.in_cutscene = True

        # On calcul où il doit aller ( 5 cases plus bas = 5 * 16 pixels = 80 pixels )
        self.cutscene_target_y = self.player.position.y + 80
        self.boss_cutscene_state = 1


    def load_boss_arena(self):
        print("--- CHARGEMENT DE L'ARÈNE DU BOSS (map_boss_1) ---")
        self.current_map_name = "map_boss_1"
        
        self.tmx_data = pytmx.load_pygame(f"assets/map/map_boss_1.tmx")
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 2.75 
        
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=6)
        
        self.collisions = []
        self.water_collisions = [] 

        for obj in self.tmx_data.objects:
            if obj.name == "collision":
                self.collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "collision1":
                self.water_collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "collision2":
                self.chests.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        self.player.add_collisions(self.collisions + self.water_collisions)
        self.group.add(self.player)
        
        self.spawn_enemies()
        self.group.center(self.player.rect.center)