import pygame
import random

from Entity import Entity
from Tool import Tool
from Bullet import Bullet

class Enemy(Entity):
    def __init__(self, screen, player, x, y, max_hp=2, points=10):
        super().__init__(None, screen, x, y)

        self.player = player
        self.spritesheet = pygame.image.load("Sprites/Personnages/Ennemie.png")
        self.image = Tool.split_image(self.spritesheet, 0, 0, 40, 40)
        self.all_images = self.get_all_images()

        ZOOM = 2
        img_frame = pygame.image.load("Sprites/ATH/spr_enemy_health_bar_frame.png").convert_alpha()
        self.health_bar_frame = pygame.transform.scale_by(img_frame, ZOOM)
        
        img_bar = pygame.image.load("Sprites/ATH/spr_enemy_health_bar.png").convert_alpha()
        self.health_bar_sprite = pygame.transform.scale_by(img_bar, ZOOM)

        # --- STATS DE COMBAT ---
        self.max_hp = max_hp
        self.hp = max_hp
        self.points = points

        # --- IA AVANCÉE ---
        self.walls = [] # Liste des murs pour la collision et la vue
        self.speed = 1

        # Vision
        self.detection_radius = 300
        self.attack_radius = 200
        self.last_seen_position = None # Où a-t-il vu le joueur pour la dernière fois ?
        
        # États : "IDLE" (Patrouille), "CHASE" (Traque), "ATTACK" (Tir)
        self.state = "IDLE"

        # Patrouille
        self.spawn_point = self.position.copy()
        self.patrol_target = self.get_random_patrol_point()
        self.wait_timer = 0
        

        # Attaque (Tir statique)
        self.shoot_cooldown = 2000
        self.last_shot_timer = 0
        self.attacking = False          # Est-il figé en train de tirer ?
        self.attack_time = 0            # Quand a-t-il commencé à tirer ?
        self.attack_stop_duration = 500 # Temps d'arrêt pendant le tir (0.5s)

        self.action_animation = 50

        # Ajouter un temps d'arrêt entre chaque case
        self.move_cooldown = 200
        self.last_move_time = 0

        try:
            self.shoot_song = pygame.mixer.Sound("musique/son_ingame/laser.wav")
            self.shoot_song.set_volume(0.3)
        except Exception as e:
            print(f"Erreur son pas: {e}")
            self.shoot_song = None


    def add_walls(self, walls):
        self.walls = walls
    
    def update(self):
        # Machine à états
        if not self.attacking:
            self.check_vision()
            
            if self.state == "ATTACK":
                self.behavior_attack()
            elif self.state == "CHASE":
                self.behavior_chase()
            elif self.state == "IDLE":
                self.behavior_idle()
        else:
            self.check_attack_end()

        super().update()
        
        # Mise à jour de l'image selon la direction
        self.image = self.all_images[self.direction][self.index_image]
        return self.shoot_if_needed()
    
    def check_attack_end(self):
        """Vérifie si l'ennemi a fini son animation de tir (arrêt)"""
        if pygame.time.get_ticks() - self.attack_time > self.attack_stop_duration:
            self.attacking = False


    def shoot_if_needed(self):
        """Gère le déclenchement du tir (retourne une balle ou None)"""
        # Si on est en mode attaque et que le timer d'arrêt vient de commencer, on tire
        if self.attacking and (pygame.time.get_ticks() - self.attack_time < 50):
             # On pourrait améliorer ça, mais pour l'instant ça marche
             if pygame.time.get_ticks() - self.last_shot_timer > self.shoot_cooldown:
                 self.last_shot_timer = pygame.time.get_ticks()
                 return self.fire_at_target(self.player.rect.center)
        return None
             
    
    def check_vision(self):
        """Vérifie si l'ennemi voit le joueur (Distance + Obstacles)"""
        dist_vector = self.player.position - self.position
        distance = dist_vector.length()

        # 1. Vérification distance
        if distance < self.detection_radius:
            # 2. Vérification obstacles
            # On trace une ligne entre l'ennemi et le joueur. Si elle coupe un mur, on ne voit pas.
            has_line_of_sight = True
            line_start = self.rect.center
            line_end = self.player.rect.center
            
            for wall in self.walls:
                if wall.clipline(line_start, line_end):
                    has_line_of_sight = False
                    break
            
            if has_line_of_sight:
                self.last_seen_position = self.player.position.copy()
                if distance < self.attack_radius:
                    self.state = "ATTACK"
                else:
                    self.state = "CHASE"
            else:
                # Si on est en CHASE mais qu'on ne voit plus, on continue vers la dernière position
                if self.state == "ATTACK": 
                    self.state = "CHASE"
        
        # Si on est en CHASE mais qu'on est arrivé à la dernière position connue sans voir le joueur
        if self.state == "CHASE" and self.last_seen_position:
            dist_to_last = (self.last_seen_position - self.position).length()
            if dist_to_last < 10:
                self.state = "IDLE" # On a perdu le joueur, on reprend la patrouille
                self.last_seen_position = None

    def behavior_attack(self):
        """Logique d'attaque : S'arrêter et tirer"""
        now = pygame.time.get_ticks()
        if now - self.last_shot_timer > self.shoot_cooldown:
            # On lance la procédure d'attaque (arrêt + tir)
            self.attacking = True
            self.attack_time = now
            self.animation_walk = False # Stop l'animation de marche
            
            # Orienter vers le joueur avant de tirer
            self.face_target(self.player.position)

    def behavior_chase(self):
        """Logique de poursuite : Aller vers la dernière position connue"""
        if self.last_seen_position:
            self.move_towards(self.last_seen_position)


    def behavior_idle(self):
        """Logique de patrouille : Aller vers un point aléatoire"""
        now = pygame.time.get_ticks()
        
        dist = (self.patrol_target - self.position).length()
        if dist < 10:
            # Arrivé au point, on attend un peu
            if self.wait_timer == 0:
                self.wait_timer = now
            elif now - self.wait_timer > 2000: # Attendre 2 sec
                self.patrol_target = self.get_random_patrol_point()
                self.wait_timer = 0
            else:
                self.animation_walk = False # On attend
        else:
            self.move_towards(self.patrol_target)


    def get_random_patrol_point(self):
        """Génère un point autour du spawn initial"""
        rx = self.spawn_point.x + random.randint(-100, 100)
        ry = self.spawn_point.y + random.randint(-100, 100)
        return pygame.math.Vector2(rx, ry)
    
    def move_towards(self, target_pos):
        """Choisit une direction et utilise le mouvement Entity si possible"""
        
        # Si on bouge déjà, on attend d'avoir fini la case
        if self.animation_walk:
            return
        
        # VERIFICATION DU DELAI
        if pygame.time.get_ticks() - self.last_move_time < self.move_cooldown:
            return

        # Calcul des différences de position
        dx = target_pos.x - self.position.x
        dy = target_pos.y - self.position.y

        # Tolérance pour éviter de trembler quand on est aligné
        if abs(dx) < 4: dx = 0
        if abs(dy) < 4: dy = 0

        if dx == 0 and dy == 0:
            return

        # Choix de la direction
        # On essaie d'abord l'axe le plus éloigné
        if abs(dx) > abs(dy):
            # Priorité Horizontale
            if dx > 0: 
                if not self.attempt_move("right"): # Si bloqué à droite...
                    self.attempt_move_vertical(dy) # ...on contourne verticalement
            else:
                if not self.attempt_move("left"):
                    self.attempt_move_vertical(dy)
        else:
            # Priorité Verticale
            if dy > 0:
                if not self.attempt_move("down"):
                    self.attempt_move_horizontal(dx) # ...on contourne horizontalement
            else:
                if not self.attempt_move("up"):
                    self.attempt_move_horizontal(dx)

    def attempt_move_vertical(self, dy):
        """Helper pour contourner verticalement"""
        if dy > 0: self.attempt_move("down")
        elif dy < 0: self.attempt_move("up")

    def attempt_move_horizontal(self, dx):
        """Helper pour contourner horizontalement"""
        if dx > 0: self.attempt_move("right")
        elif dx < 0: self.attempt_move("left")

    def attempt_move(self, direction):
        """Vérifie la collision future et lance le mouvement Entity"""
        # On anticipe la hitbox à la prochaine case (16px)
        step = 16 
        future_hitbox = self.hitbox.copy()

        if direction == "right": future_hitbox.x += step
        elif direction == "left": future_hitbox.x -= step
        elif direction == "down": future_hitbox.y += step
        elif direction == "up": future_hitbox.y -= step

        # Si collision avec un mur, on refuse le mouvement
        if future_hitbox.collidelist(self.walls) != -1:
            return False
        
        # Si c'est libre, on utilise les méthodes de Entity (animation + déplacement doux)
        if direction == "right": self.move_right()
        elif direction == "left": self.move_left()
        elif direction == "down": self.move_down()
        elif direction == "up": self.move_up()

        # On enregistre l'heure pour le prochain délai
        self.last_move_time = pygame.time.get_ticks()
        
        return True
            

    def face_direction(self, vector):
        if abs(vector.x) > abs(vector.y):
            self.direction = "right" if vector.x > 0 else "left"
        else:
            self.direction = "down" if vector.y > 0 else "up"



    def face_target(self, target_pos):
        vector = target_pos - self.position
        self.face_direction(vector)


    def fire_at_target(self, target_rect_center):
        direction_vector = pygame.math.Vector2(target_rect_center) - self.position
        if direction_vector.length() > 0:
            direction_vector = direction_vector.normalize()
        else:
            direction_vector = pygame.math.Vector2(0, 1)
            
        if self.shoot_song:
            self.shoot_song.play()
        return Bullet(self.position.x, self.position.y, direction_vector, 3, pygame.image.load("Sprites/Bullet/Enemy_bullet.png"))
    

    def damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            self.player.point += self.points
        else:
            # Si on se fait tirer dessus, on sait où est le joueur !
            self.state = "CHASE"
            self.last_seen_position = self.player.position.copy()


    def draw_health_bar(self, display, camera_pos, map_zoom):
        screen_x = (self.rect.centerx - camera_pos[0]) * map_zoom
        screen_y = (self.rect.top - camera_pos[1]) * map_zoom - 20

        frame_rect = self.health_bar_frame.get_rect(centerx=screen_x, bottom=screen_y)
        display.blit(self.health_bar_frame, frame_rect)

        if self.hp > 0:
            HEART_OFFSET_X = 7 * map_zoom
            VERTICAL_OFFSET_Y = -1 * map_zoom 
            padding_left = 4 
            
            inner_width = self.health_bar_frame.get_width() - (HEART_OFFSET_X + padding_left)
            bar_height = self.health_bar_sprite.get_height()
            
            chunk_width = inner_width / self.max_hp
            chunk_surface = pygame.transform.scale(self.health_bar_sprite, (int(chunk_width), bar_height))
            
            start_x = frame_rect.left + HEART_OFFSET_X
            start_y = frame_rect.top + (self.health_bar_frame.get_height() // 2) - (bar_height // 2) + VERTICAL_OFFSET_Y
            
            for i in range(self.hp):
                display.blit(chunk_surface, (start_x + (i * chunk_width), start_y))