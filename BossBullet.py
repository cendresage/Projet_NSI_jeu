import pygame
import math
import random

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, is_homing = False):
        super().__init__()

        # --- ETATS DE LA BALLE ---
        self.STATE_FLYING = "flying"
        self.STATE_EXPLODING = "exploding"
        self.state = self.STATE_FLYING

        # --- CHARGEMENT DES IMAGES ---
        try:
            self.sheet_bullet = pygame.image.load("Sprites/Bullet/boss_bullet.png").convert_alpha()
            # CALCUL DYNAMIQUE : On divise la largeur réelle par 4
            frame_width = self.sheet_bullet.get_width() // 4 
            self.frames_fly = self.get_frames(self.sheet_bullet, 4, frame_width, 16)
        except Exception as e:
            print(f"Erreur image balle boss: {e}")
            self.frames_fly = [pygame.Surface((16,16))]
            self.frames_fly[0].fill((255, 0, 0))

        try:
            self.sheet_smoke = pygame.image.load("Sprites/Bullet/Smoke.png").convert_alpha()
            self.frames_explode = self.get_frames_row(self.sheet_smoke, 2, 17, 64)
        except Exception as e:
            print(f"Erreur image smoke: {e}")
            self.frames_explode = [pygame.Surface((32,32))] 
            self.frames_explode[0].fill((100, 100, 100))

        try:
            self.explode_sound = pygame.mixer.Sound("musique/son_ingame/boss_impact.wav")
            self.explode_sound.set_volume(0.5) # Volume bas comme demandé (0.2)
        except:
            self.explode_sound = None

        # --- INITIALISATION ---
        self.image_index = 0
        self.image = self.frames_fly[self.image_index]
        self.rect = self.image.get_rect(center=(start_x, start_y))

        # Hitbox plus petite pour être "gentil" avec le joueur
        self.hitbox = self.rect.inflate(-5, -5)

        # Position flottante pour la précision
        self.position = pygame.math.Vector2(start_x, start_y)

        # --- MOUVEMENT ---
        self.speed = 3 if not is_homing else 2 # Plus lent si tête chercheuse
        self.is_homing = is_homing
        self.homing_timer = 0
        self.homing_duration = 1000

        # Calcul du vecteur de direction vers la cible
        direction = pygame.math.Vector2(target_x - start_x, target_y - start_y)
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = pygame.math.Vector2(1, 0) # Par défaut vers la droite

        self.animation_timer = 0
        self.animation_speed = 100

        self.damage = 1

    def get_frames(self, sheet, count, width, height):
        """Découpe une ligne simple"""
        frames = []
        for i in range(count):
            # Sécurité pour ne pas dépasser l'image
            try:
                frame = sheet.subsurface(pygame.Rect(i*width, 0, width, height))
                frames.append(frame)
            except ValueError:
                pass 
        return frames

    def get_frames_row(self, sheet, row_index, count, size):
        """Découpe une ligne spécifique pour la smoke"""
        frames = []
        # row_index commence à 0. Donc la '2ème ligne' est l'index 1
        y = (row_index - 1) * size
        for i in range(count):
            frame = sheet.subsurface(pygame.Rect(i * size, y, size, size))
            frames.append(frame)
        return frames
    
    def update(self, player=None, walls_rects=None):
        # Si on n'a pas les arguments (appel automatique map.update), on anime juste
        if player is None or walls_rects is None:
            self.animate()
            return

        # Si on a les arguments (appel manuel), on fait la logique
        self.animate()
        
        if self.state == self.STATE_FLYING:
            self.move(player, walls_rects)
            
        elif self.state == self.STATE_EXPLODING:
            pass

    def move(self, player, walls_rects):
        # Gestion tête chercheuse
        if self.is_homing:
            self.homing_timer += 16 # 1 frame à 60fps
            if self.homing_timer < self.homing_duration:
                # Ajustement de la direction vers la cible
                target_vector = pygame.math.Vector2(player.rect.centerx - self.position.x, player.rect.centery - self.position.y)
                if target_vector.lenght() > 0:
                    # On mélange l'ancienne vélocité avec la nouvelle
                    self.velocity = self.velocity.lerp(target_vector.normalize() * self.speed, 0.05)
                    self.velocity = self.velocity.normalize() * self.speed
        
        # Déplacement
        self.position += self.velocity
        self.rect.center = round(self.position.x), round(self.position.y)
        self.hitbox.center = self.rect.center

        # --- COLLISIONS ---

        # Collision Mur
        # On vérifie si la hitbox touche un mur
        if self.hitbox.collidelist(walls_rects) > -1:
            self.explode()

        # Collision Joueur
        if self.hitbox.colliderect(player.hitbox):
            player.damage(self.damage)
            self.explode()

    def explode(self):
        if self.state == self.STATE_EXPLODING:
            return
        
        if self.explode_sound:
            self.explode_sound.play()

        self.state = self.STATE_EXPLODING
        self.image_index = 0
        self.animation_speed = 50 # Explosion rapide
        self.image = self.frames_explode[self.image_index]

        # On recentre l'image car l'explosion est plus grande que la balle
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.hitbox = self.rect.inflate(-20, -20) # zone de dégats de l'explosion

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_speed:
            self.animation_timer = now

            if self.state == self.STATE_FLYING:
                self.image_index = (self.image_index + 1) % len(self.frames_fly)
                self.image = self.frames_fly[self.image_index]

            elif self.state == self.STATE_EXPLODING:
                self.image_index += 1
                if self.image_index < len(self.frames_explode):
                    self.image = self.frames_explode[self.image_index]
                else:
                    self.kill() # Animation finie, on supprime la balle