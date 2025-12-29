import pygame

from Entity import Entity

class Agis(Entity):
    def __init__(self, screen, player, x, y):
        super().__init__(None, screen, x, y)
        self.player = player

        # --- CONFIGURATION SPRITE ---
        # L'image fait 3360 de large pour 15 frames -> 3360 / 15 = 224 px par frame
        self.FRAME_WIDTH = 224
        self.FRAME_HEIGHT = 240
        self.spritesheet = pygame.image.load("Sprites/Personnages/Agis.png").convert_alpha()

        # Découpage des images
        self.all_images = self.get_images()
        self.index_image = 0
        self.image = self.all_images[self.index_image]

        # Positionnement
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.topleft = (x, y)

        # --- HITBOX SPÉCIALE (Colonne) ---
        hitbox_width = 80 
        hitbox_height = 190

        # Centre la hitbox par rapport à l'image
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.align_hitbox_custom()

        # --- ANIMATION ---
        self.animation_timer = 0
        self.animation_delay = 100

        # --- STATS ---
        self.hp = 50 # Un boss a plus de vie !
        self.max_hp = 50
        self.points = 500

    def get_images(self):
        """Découpe la grande image en 15 morceaux"""
        images = []
        for i in range(15):
            surface = self.spritesheet.subsurface(
                pygame.Rect(i * self.FRAME_WIDTH, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT)
            )
            images.append(surface)
        return images

    def update(self):
        """Logique propre au Boss"""
        self.animate()

        self.align_hitbox_custom()

        # (Logique d'attaque à ajouter plus tard)

    def animate(self):
        """Change d'image toutes les 0.1 secondes"""
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_delay:
            self.animation_timer = now
            self.index_image = (self.index_image + 1) % len(self.all_images)
            self.image = self.all_images[self.index_image]

    
    def align_hitbox_custom(self):
        """Place la hitbox au centre-bas de l'image"""
        self.rect.topleft = self.position
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom

    def damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            self.player.point += self.points
            print("Boss vaincu !!!!")

    # Pour ne pas faire planter le jeu si on essaie d'afficher sa barre de vie classique
    def draw_health_bar(self, display, camera_pos, map_zoom):
        # On pourra faire une belle barre de boss en haut de l'écran plus tard
        pass