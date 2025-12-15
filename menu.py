import pygame
import sys
from screen import Screen

ZOOM = 2

BACKGROUND_PATH = "Image/Image de fond.png"
BUTTON_IMG_PATH = "Sprites/ATH/spr_banner_hud.png"

GAMEOVER_IMG_1 = "Image/game_over1.png"
GAMEOVER_IMG_2 = "Image/game_over2.png"

WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

class ScrollingBackground:
    def __init__(self, screen_height, speed=1):
        self.image = pygame.image.load(BACKGROUND_PATH).convert()
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
        surface.blit(self.image, (self.x,0))
        surface.blit(self.image, (self.x + self.width,0))



class Button:
    def __init__(self, text, x, y, scale = 2):
        self.button_original_image = pygame.image.load(BUTTON_IMG_PATH).convert_alpha()
        
        width = self.button_original_image.get_width() * scale
        height = self.button_original_image.get_height() * scale

        self.image = pygame.transform.scale(self.button_original_image, (width, height))
        self.rect = self.image.get_rect(center = (x, y))
        self.text = text
        self.font = pygame.font.SysFont(None, 40)
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

        self.background = ScrollingBackground(self.screen.get_height(), speed = 1)
        center_x = self.screen.get_width() // 2
        start_y = 400
        gap = 80                                             #Espace entre les boutons

        self.btn_play = Button("JOUER", center_x, start_y)
        self.btn_settings = Button("PARAMETRES", center_x, start_y + gap)
        self.btn_tuto = Button("TUTORIEL", center_x, start_y + gap * 2)
        self.btn_exit = Button("QUITTER", center_x, start_y + gap * 3)

        self.buttons = [self.btn_play, self.btn_settings, self.btn_tuto, self.btn_exit]
 

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.btn_play.rect.collidepoint(mouse_pos):
                        return "play"

                    elif self.btn_settings.rect.collidepoint(mouse_pos):
                        print("Menu Paramètres à faire")

                    elif self.btn_tuto.rect.collidepoint(mouse_pos):
                        print ("Menu Tuto à faire")
                    
                    elif self.btn_exit.rect.collidepoint(mouse_pos):
                        self.running = False

        for btn in self.buttons:
            btn.update(mouse_pos)

        return None

    def run(self):
        while self.running:
            action = self.handle_input()
            if action == "play":
                return "play"
            self.background.update()
            self.background.draw(self.screen)
            
            title_font = pygame.font.SysFont(None, 100)
            title_surf = title_font.render("Laser Game", True, WHITE)
            shadow_surf = title_font.render("Laser Game", True, BLACK)

            self.screen.blit(shadow_surf, (self.screen.get_width() // 2 - title_surf.get_width() // 2 + 4, 84))
            self.screen.blit(title_surf, (self.screen.get_width() // 2 - title_surf.get_width() // 2, 80))

            for btn in self.buttons:
                btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)


class GameOverMenu:
    def __init__(self):
        self.screen_obj = Screen()
        self.screen = self.screen_obj.get_display()
        self.running = True
        self.clock = pygame.time.Clock()

        self.image = [
            pygame.image.load(GAMEOVER_IMG_1).convert(),
            pygame.image.load(GAMEOVER_IMG_2).convert()
        ]

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
        while self.running:
            action = self.handle_input()
            if action == "menu":
                return "menu"

            current_time = pygame.time.get_ticks()
            if current_time - self.animation_timer > self.animation_speed:
                self.current_image_index = (self.current_image_index + 1) % len(self.images)
                self.animation_timer = current_time
            
            self.screen.blit(self.images[self.current_image_index], (0, 0))
            self.btn_menu.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)
                