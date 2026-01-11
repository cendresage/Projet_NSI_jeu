import pygame
import random
import os

from Entity import Entity
from BossBullet import BossBullet
from SoundManager import SoundManager

class Agis(Entity):
    def __init__(self, screen, player, x, y):
        super().__init__(None, screen, x, y)
        self.player = player
        self._layer = 5

        # --- CONFIGURATION SPRITE ---
        # L'image fait 3360 de large pour 15 frames -> 3360 / 15 = 224 px par frame
        self.FRAME_WIDTH = 224
        self.FRAME_HEIGHT = 240
        
        image_path = "Sprites/Personnages/Agis.png"
        try:
            self.spritesheet = pygame.image.load(image_path).convert_alpha()
            self.all_images = self.get_images()
        except Exception as e:
            print(f"\n[ERREUR BOSS] Impossible de charger l'image : {image_path}")
            print(f"Erreur Python : {e}")
            print(f"Dossier actuel de travail : {os.getcwd()}") # Affiche le dossier utilisé par le jeu
            print("-> Le boss sera un carré noir pour éviter le crash.\n")
            
            # Carré noir de secours
            self.all_images = [pygame.Surface((224, 240))]
            self.all_images[0].fill((0, 0, 0))

        try:
            self.sheet_smoke = pygame.image.load("Sprites/Bullet/Smoke.png").convert_alpha()
            self.death_frames = self.get_frames_row(self.sheet_smoke, 6, 17, 64)
        except Exception as e:
            print(f"Erreur chargement smoke boss: {e}")
            self.death_frames = []

        self.index_image = 0
        self.image = self.all_images[self.index_image]

        # Positionnement
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.topleft = (x, y)

        # --- HITBOX ---
        self.hitbox = pygame.Rect(0, 0, 80, 190)
        self.align_hitbox_custom()

        # --- ANIMATION ---
        self.animation_timer = 0
        self.animation_delay = 100

        # --- STATS ---
        self.hp = 50
        self.max_hp = 50
        self.points = 500

        # --- ETAT MORT ---
        self.is_dying = False
        self.death_timer = 0
        self.death_index = 0
        self.death_delay = 60 # Vitesse de l'animation de mort

        # --- Attaque ---
        self.attack_timer = pygame.time.get_ticks()
        self.last_phase = 1 # détection de changement de phase
        self.hands_offsets = [
            (20, 60),   # Main Haut Gauche
            (200, 60),  # Main Haut Droite
            (40, 120),  # Main Bas Gauche
            (180, 120)  # Main Bas Droite
        ]

        try:
            self.shoot_sound = pygame.mixer.Sound(SoundManager.get_path("boss_shot")) # Vérifie le nom du fichier !
            self.shoot_sound.set_volume(0.6)
        except Exception as e:
            print(f"Erreur son boss shoot: {e}")
            self.shoot_sound = None

        try:
            self.bar_img = pygame.image.load("Sprites/ATH/boss_bar.png").convert_alpha()
        except:
            print("Erreur : Image barre boss non trouvée")
            self.bar_img = None

        self.font_boss = pygame.font.SysFont("Arial", 24, bold=True)
            

    def get_images(self):
        """Découpe la grande image en 15 morceaux"""
        images = []
        for i in range(15):
            surface = self.spritesheet.subsurface(
                pygame.Rect(i * self.FRAME_WIDTH, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT)
            )
            images.append(surface)
        return images
    
    def get_frames_row(self, sheet, row_index, count, size):
        frames = []
        y = (row_index - 1) * size 
        for i in range(count):
            try:
                frame = sheet.subsurface(pygame.Rect(i*size, y, size, size))
                frames.append(frame)
            except ValueError: pass
        return frames

    def update(self, current_time=None, bullet_group=None, walls=None):
        """Logique propre au Boss"""
        
        # Cas 1 : Appelé par Map.py (automatique, sans arguments)
        # On ne fait rien pour ne pas planter, ou juste l'animation simple.
        if current_time is None or bullet_group is None or walls is None:
            return
        
        # Si le boss est en train de mourir, on joue SEULEMENT l'animation de mort
        if self.is_dying:
            self.animate_death(current_time)
            return

        # Comportement normal
        if bullet_group is None or walls is None:
            return

        # Cas 2 : Appelé par Game1.py (manuel, avec arguments)
        # Là on lance toute la logique de combat
        
        # Animation
        if current_time - self.animation_timer > self.animation_delay:
            self.animation_timer = current_time
            self.index_image = (self.index_image + 1) % len(self.all_images)
            self.image = self.all_images[self.index_image]

        # Combat
        self.manage_combat(current_time, bullet_group)
        self.align_hitbox_custom()

    def manage_combat(self, current_time, bullet_group):
        # Détermination de la phase
        phase = 1
        attack_cooldown = 2200
        is_homing = False

        if 10 < self.hp <= 25:
            phase = 2 
            attack_cooldown = 1500
        elif self.hp <= 10:
            phase = 3
            attack_cooldown = 1200
            is_homing = True

        # Détection changement de phase
        if phase != self.last_phase:
            self.roar()
            self.last_phase = phase

        # Tirer si le timer est bon
        if current_time - self.attack_timer > attack_cooldown:
            self.attack_timer = current_time
            self.shoot(bullet_group, is_homing)

    def shoot(self, bullet_group, is_homing):
        # Choisir une main au hasard
        offset_x, offset_y = random.choice(self.hands_offsets)

        start_x = self.rect.x + offset_x
        start_y = self.rect.y + offset_y

        # Viser le joueur
        target_x = self.player.rect.centerx
        target_y = self.player.rect.centery

        bullet = BossBullet(start_x, start_y, target_x, target_y, is_homing)

        bullet_group.add(bullet)

        if self.shoot_sound:
            self.shoot_sound.play()

    def roar(self):
        try:
            sound = pygame.mixer.Sound(SoundManager.get_path("roar"))
            sound.set_volume(5.0)
            sound.play()
        except:
            pass


    
    def align_hitbox_custom(self):
        """Place la hitbox au centre-bas de l'image"""
        self.rect.topleft = self.position
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom

    def damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_dying = True
            self.player.point += self.points
            # On fait un fondu de 2 secondes pour un rendu fluide
            pygame.mixer.music.fadeout(2000)
            self.roar()
            
            # On annule la hitbox pours que les balles passent à travers
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            print("Boss vaincu - Animation de mort lancée")

    def animate_death(self, current_time):
        if current_time - self.death_timer > self.death_delay:
            self.death_timer = current_time

            # SI c'est la première frame de mort, on passe sur l'image de fumée
            if self.death_index == 0 and self.death_frames:
                self.image = self.death_frames[0]
                # On recentre l'image car la fumée est plus petite que le boss
                old_center = self.rect.center
                self.rect = self.image.get_rect(center=old_center)

            # On avance dans l'animation
            self.death_index += 1
            if self.death_index < len(self.death_frames):
                self.image = self.death_frames[self.death_index]
            else:
                self.kill()
            

    def draw_health_bar(self, display, camera_pos, map_zoom):
        if self.is_dying: 
            return

        screen_w, screen_h = display.get_size()

        if self.bar_img:
            bar_rect = self.bar_img.get_rect(midbottom=(screen_w // 2, screen_h - 10))

            # --- REGLAGES DE LA ZONE ROUGE ---
            padding_left = 45   # Marge à gauche
            padding_right = 45  # Marge à droite
            padding_top = 13    # Marge en haut (dans le cadre)
            padding_bottom = 13 # Marge en bas

            inner_width = bar_rect.width - (padding_left + padding_right)
            inner_height = self.bar_img.get_height() - (padding_top + padding_bottom)

            ratio = self.hp / self.max_hp
            if ratio < 0:
                ratio = 0
            current_bar_width = int(inner_width * ratio)

            health_rect = pygame.Rect(
                bar_rect.x + padding_left,
                bar_rect.y + padding_top,
                current_bar_width,
                inner_height
            )
            
            #  Dessiner la vie (Rouge sombre derrière)
            # On dessine un fond noir d'abord pour "boucher" le trou transparent si la vie baisse
            bg_rect = pygame.Rect(bar_rect.x + padding_left, bar_rect.y + padding_top, inner_width, inner_height)
            pygame.draw.rect(display, (20, 0, 0), bg_rect)

            # On dessine ensuite la barre de vie
            if current_bar_width > 0:
                pygame.draw.rect(display, (180, 0, 0), health_rect)

            # Dessiner le cadre
            display.blit(self.bar_img, bar_rect)

            # Position du texte
            text_y_pos = bar_rect.top - 25
        else:
            # Fallback (Si l'image ne charge pas)
            bar_width = 600
            x = (screen_w - bar_width) // 2
            y = screen_h - 60
            pygame.draw.rect(display, (50, 50, 50), (x, y, bar_width, 20))
            ratio = self.hp / self.max_hp
            pygame.draw.rect(display, (180, 0, 0), (x, y, bar_width * ratio, 20))
            text_y_pos = y - 35
        
        name = "AGIS - LE GARDIEN D'AME"
        shadow_surf = self.font_boss.render(name, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(screen_w // 2 + 2, text_y_pos + 2))
        display.blit(shadow_surf, shadow_rect)

        text_surf = self.font_boss.render(name, True, (255, 215, 0))
        text_rect = text_surf.get_rect(center=(screen_w // 2, text_y_pos))
        display.blit(text_surf, text_rect)