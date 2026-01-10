import pygame
import sys
import json
import os

from Screen import Screen
from Keylistener import Keylistener
from Music import Music

ZOOM = 2

BACKGROUND_PATH = "Image/Image de fond.png"
BUTTON_IMG_PATH = "Sprites/ATH/spr_banner_hud.png"

GAMEOVER_IMGS = ["Image/game_over1.png", "Image/game_over2.png"]
TIMEOUT_IMGS = ["Image/time_elapsed1.png", "Image/time_elapsed2.png"]
WIN_IMGS = ["Image/Win1.png", "Image/Win2.png"]

WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)

class ScrollingBackground:
    def __init__(self, screen_height, speed=1):
        try:
            self.image = pygame.image.load(BACKGROUND_PATH).convert()
        except:
            self.image = pygame.Surface((800, 600))
            self.image.fill((50, 50, 100))

        self.speed = speed
        ratio = screen_height / self.image.get_height()
        new_width = int(self.image.get_width() * ratio)
        new_height = int(self.image.get_height() * ratio)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.width = self.image.get_width()
        self.x = 0

    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            self.x = 0

    def draw(self, surface):
        surface.blit(self.image, (self.x, 0))
        surface.blit(self.image, (self.x + self.width, 0))

class Button:
    def __init__(self, text, x, y, scale=2, font_size=40):
        try:
            self.button_original_image = pygame.image.load(BUTTON_IMG_PATH).convert_alpha()
        except:
            self.button_original_image = pygame.Surface((100, 40))
            self.button_original_image.fill((100, 100, 100))

        width = self.button_original_image.get_width() * scale
        height = self.button_original_image.get_height() * scale
        self.image = pygame.transform.scale(self.button_original_image, (int(width), int(height)))
        self.rect = self.image.get_rect(center=(x, y))
        self.text = text
        self.font = pygame.font.SysFont(None, font_size)
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        color = GOLD if self.is_hovered else WHITE
        text_surf = self.font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        shadow_surf = self.font.render(self.text, True, BLACK)
        surface.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2 - 3))
        surface.blit(text_surf, (text_rect.x, text_rect.y))

class Menu:
    def __init__(self):
        self.screen_obj = Screen()
        self.screen = self.screen_obj.get_display()
        self.running = True
        self.clock = pygame.time.Clock()

        # Outils
        self.music = Music()
        self.keylistener = Keylistener()

        self.background = ScrollingBackground(self.screen.get_height(), speed=1)
        
        # --- ETAT DU MENU ---
        self.state = "main" # "main" ou "settings"
        self.waiting_key_action = None # Pour remapper les touches

        # --- BOUTONS MENU PRINCIPAL ---
        center_x = self.screen.get_width() // 2
        start_y = 400
        gap = 80
        self.btn_play = Button("JOUER", center_x, start_y)
        self.btn_settings = Button("PARAMETRES", center_x, start_y + gap)
        self.btn_tuto = Button("TUTORIEL", center_x, start_y + gap * 2)
        self.btn_exit = Button("QUITTER", center_x, start_y + gap * 3)
        self.buttons = [self.btn_play, self.btn_settings, self.btn_tuto, self.btn_exit]

        # --- ELEMENTS MENU PARAMETRES ---
        # Panneau de fond
        try:
            base_banner = pygame.image.load(BUTTON_IMG_PATH).convert_alpha()
            self.panel_img = pygame.transform.scale(self.panel_img, (600, 500))
            self.control_row_img = pygame.transform.scale(base_banner, (480, 55))
        except:
            self.panel_img = pygame.Surface((600, 500))
            self.panel_img.fill((50, 50, 80))
            self.control_row_img = pygame.Surface((480, 55))
            self.control_row_img.fill((70, 70, 100))
        
        self.panel_rect = self.panel_img.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        
        # Bouton Retour (dans les paramètres)
        self.btn_back = Button("RETOUR", self.panel_rect.centerx, self.panel_rect.bottom - 50, scale=1.5, font_size=30)

        self.settings_start_y_offset = 170 
        self.settings_gap_y = 65

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            # --- GESTION CHANGEMENT DE TOUCHE ---
            if self.waiting_key_action:
                if event.type == pygame.KEYDOWN:
                    self.keylistener.controls[self.waiting_key_action] = event.key
                    self.keylistener.save_controls() # Sauvegarde immédiate
                    self.waiting_key_action = None
                return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # SI ON EST DANS LE MENU PRINCIPAL
                    if self.state == "main":
                        if self.btn_play.rect.collidepoint(mouse_pos):
                            return "play"
                        elif self.btn_settings.rect.collidepoint(mouse_pos):
                            self.state = "settings"
                        elif self.btn_exit.rect.collidepoint(mouse_pos):
                            self.running = False
                    
                    # SI ON EST DANS LES PARAMETRES
                    elif self.state == "settings":
                        if self.btn_back.rect.collidepoint(mouse_pos):
                            self.state = "main"
                        
                        # Gestion Volume (+ / -)
                        vol_minus = pygame.Rect(self.panel_rect.right - 180, self.panel_rect.top + 80, 40, 40)
                        vol_plus = pygame.Rect(self.panel_rect.right - 80, self.panel_rect.top + 80, 40, 40)
                        
                        if vol_minus.collidepoint(mouse_pos):
                            self.music.change_volume(-0.1)
                        if vol_plus.collidepoint(mouse_pos):
                            self.music.change_volume(0.1)

                        # Gestion Touches (Clic sur le texte)
                        actions = ["up", "down", "left", "right"]
                        start_y = self.panel_rect.top + 160
                        for i, action in enumerate(actions):
                            rect = pygame.Rect(self.panel_rect.x + 50, start_y + i*50, 400, 40)
                            if rect.collidepoint(mouse_pos):
                                self.waiting_key_action = action

        # Mise à jour survol boutons
        if self.state == "main":
            for btn in self.buttons:
                btn.update(mouse_pos)
        elif self.state == "settings":
            self.btn_back.update(mouse_pos)

        return None

    def draw_settings(self):
        # Fond sombre
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(150)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        # Panneau
        self.screen.blit(self.panel_img, self.panel_rect)

        # Titre
        font_title = pygame.font.SysFont(None, 60, bold=True)
        title = font_title.render("PARAMETRES", True, WHITE)
        self.screen.blit(title, (self.panel_rect.centerx - title.get_width()//2, self.panel_rect.top + 30))

        # --- VOLUME ---
        font_text = pygame.font.SysFont(None, 40)
        vol_text = font_text.render(f"Musique: {int(self.music.volume * 100)}%", True, WHITE)
        self.screen.blit(vol_text, (self.panel_rect.x + 50, self.panel_rect.top + 90))

        # Boutons Volume Fake (juste visuels ici, la logique est dans handle_input)
        min_rect = pygame.Rect(self.panel_rect.right - 180, self.panel_rect.top + 80, 40, 40)
        plus_rect = pygame.Rect(self.panel_rect.right - 80, self.panel_rect.top + 80, 40, 40)
        pygame.draw.rect(self.screen, (200, 50, 50), min_rect)
        pygame.draw.rect(self.screen, (50, 200, 50), plus_rect)
        self.screen.blit(font_text.render("-", True, WHITE), (min_rect.x + 13, min_rect.y + 5))
        self.screen.blit(font_text.render("+", True, WHITE), (plus_rect.x + 10, plus_rect.y + 5))

        # --- TOUCHES ---
        actions = ["up", "down", "left", "right"]
        labels = ["Avancer", "Reculer", "Gauche", "Droite"]
        start_y = self.panel_rect.top + 170
        gap_y = 65

        font_controls = pygame.font.SysFont(None, 35)
        
        for i, action in enumerate(actions):
            row_center_y = start_y + i * gap_y
            
            # Dessiner la bannière de fond pour la ligne
            row_rect = self.control_row_img.get_rect(center=(self.panel_rect.centerx, row_center_y))
            self.screen.blit(self.control_row_img, row_rect)

            # Préparer le texte
            key_code = self.keylistener.controls.get(action, 0)
            key_name = pygame.key.name(key_code).upper()
            
            color = (255, 255, 0) if self.waiting_key_action == action else WHITE
            text_str = f"{labels[i]} : {key_name}"
            if self.waiting_key_action == action:
                text_str = f"{labels[i]} : APPUIE SUR UNE TOUCHE..."

            # Dessiner le texte centré sur la bannière
            text_img = font_controls.render(text_str, True, color)
            text_rect = text_img.get_rect(center=row_rect.center)
            self.screen.blit(text_img, text_rect)

        # Bouton retour
        self.btn_back.draw(self.screen)

    def run(self):
        self.music.play("menu")
        
        while self.running:
            action = self.handle_input()
            if action == "play":
                self.music.stop()
                return "play"
            
            self.background.update()
            self.background.draw(self.screen)
            
            # Si Menu Principal
            if self.state == "main":
                title_font = pygame.font.SysFont(None, 100)
                title_surf = title_font.render("Laser Game", True, WHITE)
                shadow_surf = title_font.render("Laser Game", True, BLACK)
                self.screen.blit(shadow_surf, (self.screen.get_width() // 2 - title_surf.get_width() // 2 + 4, 84))
                self.screen.blit(title_surf, (self.screen.get_width() // 2 - title_surf.get_width() // 2, 80))

                for btn in self.buttons:
                    btn.draw(self.screen)
            
            # Si Paramètres
            elif self.state == "settings":
                self.draw_settings()

            pygame.display.flip()
            self.clock.tick(60)

class EndMenu:
    def __init__(self, score, result_type="dead"):
        self.screen_obj = Screen()
        self.screen = self.screen_obj.get_display()
        self.running = True
        self.clock = pygame.time.Clock()

        self.music = Music()

        self.score = score
        self.highscore = self.load_highscore()
        self.new_record = False
        
        if self.score > self.highscore:
            self.highscore = self.score
            self.new_record = True
            self.save_highscore()

        self.font_score = pygame.font.SysFont(None, 40, bold=True)
        self.font_title = pygame.font.SysFont(None, 60, bold=True)
        self.result_type = result_type

        img_paths = GAMEOVER_IMGS
        sound_track = "game_over"

        if result_type == "time_out":
            img_paths = TIMEOUT_IMGS
            sound_track = "game_over"
        elif result_type == "win":
            img_paths = WIN_IMGS
            sound_track = "menu"

        try:
            self.music.play(sound_track)
        except:
            pass


        try:
            self.image = [pygame.image.load(p).convert() for p in img_paths]
        except:
            self.image = [pygame.Surface((800,600)), pygame.Surface((800,600))]
            self.image[0].fill((0,0,0))
            self.image[1].fill((20,20,20))

        self.images = [
            pygame.transform.scale(img, (self.screen.get_width(), self.screen.get_height()))
            for img in self.image
        ]

        self.current_image_index = 0
        self.animation_timer = 0
        self.animation_speed = 500

        center_x = self.screen.get_width() // 2
        bottom_y = self.screen.get_height() - 100
        self.btn_menu = Button("Menu", center_x, bottom_y)

    def load_highscore(self):
        path = "assets/data/highscore.json"
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    return data.get("highscore", 0)
            except:
                return 0
        return 0
    
    def save_highscore(self):
        path = "assets/data/highscore.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump({"highscore": self.highscore}, f)

    def draw(self):
        self.screen.blit(self.images[self.current_image_index], (0, 0))
        center_x = self.screen.get_width() // 2

        txt_score = self.font_score.render(f"Score: {self.score}", True, (255, 255, 255))
        rect_score = txt_score.get_rect(center=(center_x, 300))
        self.screen.blit(txt_score, rect_score)

        color = (255, 215, 0) if self.new_record else (200, 200, 200)
        txt_best = self.font_score.render(f"Best: {self.highscore}", True, color)
        rect_best = txt_best.get_rect(center=(center_x, 360))
        self.screen.blit(txt_best, rect_best)

        if self.new_record:
            txt_record = self.font_title.render("NOUVEAU RECORD !", True, (255, 215, 0))
            rect_record = txt_record.get_rect(center=(center_x, 200))
            self.screen.blit(txt_record, rect_record)

        self.btn_menu.draw(self.screen)

    def fade_in(self):
        fade_surface = pygame.Surface(self.screen.get_size())
        fade_surface.fill((0, 0, 0))

        for alpha in range(255, 0,-5):
            fade_surface.set_alpha(alpha)
            self.draw()
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(20)

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.btn_menu.rect.collidepoint(mouse_pos):
                        return "menu"
        self.btn_menu.update(mouse_pos)
        return None

    def run(self):
        self.fade_in()
        while self.running:
            action = self.handle_input()
            if action == "menu":
                self.music.stop()
                return "menu"

            current_time = pygame.time.get_ticks()
            if current_time - self.animation_timer > self.animation_speed:
                self.current_image_index = (self.current_image_index + 1) % len(self.images)
                self.animation_timer = current_time
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)