import pygame

from Screen import Screen
from Keylistener import Keylistener
from Music import Music
from Button import *
from ScrollingBackground import ScrollingBackground
from Tutorial import Tutorial
from SoundManager import SoundManager

class Menu:
    def __init__(self):
        self.screen_obj = Screen()
        self.screen = self.screen_obj.get_display()
        self.running = True
        self.clock = pygame.time.Clock()

        self.music = Music()
        self.keylistener = Keylistener()

        self.background = ScrollingBackground(self.screen.get_height(), speed=1)
        
        self.tutorial = Tutorial(self.screen)
        self.state = "main"
        self.waiting_key_action = None

        # --- KONAMI CODE VARIABLES ---
        self.konami_code = [
            pygame.K_UP, pygame.K_UP, 
            pygame.K_DOWN, pygame.K_DOWN, 
            pygame.K_LEFT, pygame.K_RIGHT, 
            pygame.K_LEFT, pygame.K_RIGHT
        ]
        self.key_history = []
        # -----------------------------
        
        center_x = self.screen.get_width() // 2
        start_y = 400
        gap = 80
        self.btn_play = Button("JOUER", center_x, start_y)
        self.btn_settings = Button("PARAMETRES", center_x, start_y + gap)
        self.btn_tuto = Button("TUTORIEL", center_x, start_y + gap * 2)
        self.btn_exit = Button("QUITTER", center_x, start_y + gap * 3)
        self.buttons = [self.btn_play, self.btn_settings, self.btn_tuto, self.btn_exit]

        
        self.panel_rect = pygame.Rect(0, 0, 600, 500)
        self.panel_rect.center = (self.screen.get_width()//2, self.screen.get_height()//2)

        self.btn_back = Button("RETOUR", self.panel_rect.centerx, self.panel_rect.bottom - 50, scale=1.5, font_size=30)
        
        self.settings_start_y_offset = 170
        self.settings_gap_y = 65

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "exit"
            
            # Gestion du Konami Code (uniquement dans le menu principal)
            if event.type == pygame.KEYDOWN:
                self.key_history.append(event.key)
                # On garde seulement les X dernières touches (taille du code)
                if len(self.key_history) > len(self.konami_code):
                    self.key_history.pop(0)
                
                # Vérification
                if self.key_history == self.konami_code:
                    SoundManager.toggle_secret_mode()
                    self.key_history = [] # Reset pour éviter double activation
                    # On relance la musique pour entendre le changement tout de suite
                    self.music.stop()
                    self.music.play("menu")

            # --- GESTION DU CLIC POUR LE TUTO ---
            # Si le tuto est ouvert, il prend la priorité sur tout le reste
            if self.tutorial.active:
                self.tutorial.handle_input(event)
                return None # On ne traite rien d'autre tant que le tuto est là

            if self.waiting_key_action:
                if event.type == pygame.KEYDOWN:
                    self.keylistener.controls[self.waiting_key_action] = event.key
                    self.keylistener.save_controls()
                    self.waiting_key_action = None
                return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.state == "main":
                        if self.btn_play.rect.collidepoint(mouse_pos):
                            return "play"
                        elif self.btn_settings.rect.collidepoint(mouse_pos):
                            self.state = "settings"
                        elif self.btn_tuto.rect.collidepoint(mouse_pos):
                            self.tutorial.start()
                        elif self.btn_exit.rect.collidepoint(mouse_pos):
                            self.running = False
                            return "exit"
                    
                    elif self.state == "settings":
                        if self.btn_back.rect.collidepoint(mouse_pos):
                            self.state = "main"
                        
                        vol_minus = pygame.Rect(self.panel_rect.right - 180, self.panel_rect.top + 80, 40, 40)
                        vol_plus = pygame.Rect(self.panel_rect.right - 80, self.panel_rect.top + 80, 40, 40)
                        
                        if vol_minus.collidepoint(mouse_pos):
                            self.music.change_volume(-0.1)
                        if vol_plus.collidepoint(mouse_pos):
                            self.music.change_volume(0.1)

                        actions = ["up", "down", "left", "right"]
                        start_y = self.panel_rect.top + self.settings_start_y_offset
                        
                        for i, action in enumerate(actions):
                            row_center_y = start_y + i * self.settings_gap_y
                            rect = pygame.Rect(0, 0, 480, 55)
                            rect.center = (self.panel_rect.centerx, row_center_y)
                            if rect.collidepoint(mouse_pos):
                                self.waiting_key_action = action

        if self.state == "main":
            for btn in self.buttons:
                btn.update(mouse_pos)
        elif self.state == "settings":
            self.btn_back.update(mouse_pos)

        return None

    def draw_settings(self):
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(150)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        font_title = pygame.font.SysFont(None, 60, bold=True)
        title = font_title.render("PARAMETRES", True, WHITE)
        self.screen.blit(title, (self.panel_rect.centerx - title.get_width()//2, self.panel_rect.top + 30))

        font_text = pygame.font.SysFont(None, 40)
        vol_text = font_text.render(f"Musique: {int(self.music.volume * 100)}%", True, WHITE)
        self.screen.blit(vol_text, (self.panel_rect.x + 50, self.panel_rect.top + 90))

        # Bouton Volume
        min_rect = pygame.Rect(self.panel_rect.right - 180, self.panel_rect.top + 80, 40, 40)
        plus_rect = pygame.Rect(self.panel_rect.right - 80, self.panel_rect.top + 80, 40, 40)
        pygame.draw.rect(self.screen, (200, 50, 50), min_rect)
        pygame.draw.rect(self.screen, (50, 200, 50), plus_rect)
        self.screen.blit(font_text.render("-", True, WHITE), (min_rect.x + 13, min_rect.y + 5))
        self.screen.blit(font_text.render("+", True, WHITE), (plus_rect.x + 10, plus_rect.y + 5))

        actions = ["up", "down", "left", "right"]
        labels = ["Avancer", "Reculer", "Gauche", "Droite"]
        start_y = self.panel_rect.top + self.settings_start_y_offset
        font_controls = pygame.font.SysFont(None, 35)

        for i, action in enumerate(actions):
            row_center_y = start_y + i * self.settings_gap_y
            
            # Rectangle virtuel pour le centrage
            row_rect = pygame.Rect(0, 0, 480, 55)
            row_rect.center = (self.panel_rect.centerx, row_center_y)

            key_code = self.keylistener.controls.get(action, 0)
            key_name = pygame.key.name(key_code).upper()
            
            # Couleur change si on est en train de modifier la touche
            color = (255, 255, 0) if self.waiting_key_action == action else WHITE
            
            text_str = f"{labels[i]} : {key_name}"
            if self.waiting_key_action == action:
                text_str = f"{labels[i]} : APPUIE SUR UNE TOUCHE..."

            text_img = font_controls.render(text_str, True, color)
            text_rect = text_img.get_rect(center=row_rect.center)
            self.screen.blit(text_img, text_rect)

        # 5. Bouton Retour (Lui a le droit d'avoir une image)
        self.btn_back.draw(self.screen)

    def run(self):
        self.music.play("menu")
        while self.running:
            action = self.handle_input()
            if action == "play":
                self.music.stop()
                return "play"
            if action == "exit":
                return "exit"
            
            self.background.update()
            self.background.draw(self.screen)
            
            if self.state == "main":
                title_font = pygame.font.SysFont(None, 100)
                title_surf = title_font.render("Laser Game", True, WHITE)
                shadow_surf = title_font.render("Laser Game", True, BLACK)
                self.screen.blit(shadow_surf, (self.screen.get_width() // 2 - title_surf.get_width() // 2 + 4, 84))
                self.screen.blit(title_surf, (self.screen.get_width() // 2 - title_surf.get_width() // 2, 80))
                for btn in self.buttons:
                    btn.draw(self.screen)
            elif self.state == "settings":
                self.draw_settings()

            if self.tutorial.active:
                self.tutorial.draw()

            pygame.display.flip()
            self.clock.tick(60)
        return "exit"

            