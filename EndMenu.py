import pygame
import sys
import json
import os

from Screen import Screen
from Music import Music
from Button import Button  # On importe le bouton optimisé

# Images pour les différentes fins
GAMEOVER_IMGS = ["Image/game_over1.png", "Image/game_over2.png"]
TIMEOUT_IMGS = ["Image/time_elapsed1.png", "Image/time_elapsed2.png"]
WIN_IMGS = ["Image/Win1.png", "Image/Win2.png"]

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

        # Choix des images et de la musique
        img_paths = GAMEOVER_IMGS
        title_text = "GAME OVER"
        title_color = (255, 0, 0)
        sound_track = "game_over" 

        if result_type == "time_out":
            img_paths = TIMEOUT_IMGS
            title_text = "TEMPS ECOULE"
            title_color = (255, 100, 0)
            sound_track = "game_over" 
        elif result_type == "win":
            img_paths = WIN_IMGS
            title_text = "VICTOIRE !"
            title_color = (0, 255, 0)
            sound_track = "menu"

        # Lancement de la musique
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
        
        self.title_text_render = self.font_title.render(title_text, True, title_color)

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
            except: return 0
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