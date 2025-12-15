import pygame

from screen import Screen
from map import Map
from entity import Entity
from keylistener import Keylistener
from player import Player
from enemy import Enemy

HUD_SCALE = 2

PLAYER_STATUS_BG_PATH = "Sprites/ATH/spr_player_status_version1.png"
HEALTHBAR_PATH = "Sprites/ATH/spr_player_status_healthbar_bk.png"
MONEY_ICON_PATH = "Sprites/ATH/spr_money_interface.png"

class Game:
    def __init__(self):
        self.running = True
        self.screen = Screen()
        self.map = Map(self.screen)
        self.keylistener = Keylistener()
        self.Player = Player(self.keylistener, self.screen, 0, 0)
        self.map.add_player(self.Player)
        self.player_bullets = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 18, bold=True)

        self.hud_bg_img = pygame.transform.scale_by(
            pygame.image.load(PLAYER_STATUS_BG_PATH).convert_alpha(), HUD_SCALE
        )
        self.health_bar_img = pygame.transform.scale_by(
            pygame.image.load(HEALTHBAR_PATH).convert_alpha(), HUD_SCALE
        )
        self.money_icon_img = pygame.transform.scale_by(
            pygame.image.load(MONEY_ICON_PATH).convert_alpha(), HUD_SCALE
        )

        self.player_head_img = self._get_player_head_image()

        # Temporaire 
        self.ennemi1 = Enemy(self.screen, self.Player, 200, 200)
        self.map.group.add(self.ennemi1)
        self.enemy_group.add(self.ennemi1)


    def _get_player_head_image(self):
        player_spritesheet = pygame.image.load("Sprites/Personnages/Player.png")
        
        # Extrait la tête non mise à l'échelle (16x16)
        head_surface_unscaled = player_spritesheet.subsurface(pygame.Rect(12, 2, 16, 16)).convert_alpha()
        return pygame.transform.scale(head_surface_unscaled, (16 * HUD_SCALE, 16 * HUD_SCALE))



    def run(self):
        while self.running:
            if self.Player.hp <= 0:
                return "game_over"
                
            self.handle_input()

            for enemy in self.enemy_group:
                new_bullet = enemy.update()
                if new_bullet:
                    self.map.group.add(new_bullet)
                    self.enemy_bullets.add(new_bullet)

            hits = pygame.sprite.groupcollide(
                self.enemy_group, 
                self.player_bullets, 
                False, 
                True,  
                collided=self.check_collision_hitbox 
            )
            for enemy in hits:
                enemy.damage(1)

            hits_player = pygame.sprite.spritecollide(
                self.Player, 
                self.enemy_bullets, 
                True, 
                collided=self.check_collision_hitbox
            )
            for bullet in hits_player:
                self.Player.damage(1)

            all_bullets = self.player_bullets.copy()
            all_bullets.add(self.enemy_bullets)

            self.map.update(all_bullets)
            
            self.draw_hud()
            
            camera_pos = self.map.group.view.topleft
            map_zoom = self.map.map_layer.zoom
            for enemy in self.enemy_group:
                enemy.draw_health_bar(self.screen.get_display(), camera_pos, map_zoom)
            
            self.screen.update()
        
        return "quit"

    def check_collision_hitbox(self, sprite1, sprite2):
        return sprite1.hitbox.colliderect(sprite2.hitbox)

    def handle_input(self):
        for event in pygame.event.get():                # Gestion des évènements (récupère les touches pressées)
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                self.keylistener.add_key(event.key)
            elif event.type == pygame.KEYUP:
                self.keylistener.remove_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:                   # Bouton gauche de la souris
                    new_bullet = self.Player.fire()
                    self.player_bullets.add(new_bullet)
                    self.map.group.add(new_bullet)


    def draw_hud(self):
        display = self.screen.get_display()

        # Constantes d'alignement
        BASE_X = 20
        BASE_Y = 20

        display.blit(self.hud_bg_img, (BASE_X, BASE_Y))

        head_x = BASE_X + (9 * HUD_SCALE) 
        head_y = BASE_Y + (6 * HUD_SCALE)
        display.blit(self.player_head_img, (head_x, head_y))

        hp_bar_x = BASE_X + (33 * HUD_SCALE)
        hp_bar_y = BASE_Y + (12 * HUD_SCALE)

        if self.Player.max_hp > 0:
            ratio = self.Player.hp / self.Player.max_hp
            full_width = self.health_bar_img.get_width()
            full_height = self.health_bar_img.get_height()
            visible_width = int(full_width * ratio)
            if visible_width > 0:
                area_rect = pygame.Rect(0, 0, visible_width, full_height)
                display.blit(self.health_bar_img, (hp_bar_x, hp_bar_y), area_rect)

        money_y = BASE_Y + self.hud_bg_img.get_height() + 5 
        money_x = BASE_X

        display.blit(self.money_icon_img, (money_x, money_y))

        score_x = money_x + 60 
        score_y = money_y + (self.money_icon_img.get_height() // 2) - (self.small_font.get_height() // 2)
        
        score_text = self.small_font.render(f"{self.Player.point}", True, (255, 255, 255))
        display.blit(score_text, (score_x, score_y))

    
    def fade_out_game_over(self):
        display_surface = self.screen.get_display()

        # Prend l'écran actuel pour le figer
        snapshot = display_surface.copy()
        
        # Surface noir transparente pour le fondu
        fade_surface = pygame.Surface(display_surface.get_size())
        fade_surface.fill((0, 0, 0))

        # Boucle de fondu
        for alpha in range(0, 255, 5):
            fade_surface.set_alpha(alpha)

            display_surface.blit(snapshot, (0, 0))
            display_surface.blit(fade_surface, (0, 0))

            self.screen.update()
            pygame.time.delay(20)