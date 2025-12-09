import pygame
import sys
from screen import Screen


BACKGROUND_PATH = "Image/Image de fond.png"
BUTTON_IMG_PATH = "Sprites/ATH/spr_banner_hud.png"

WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
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

    def draw(self, screen):
        surface.blit(self.image, (self.x,0))
        surface.blit(self.image, (self.x + self.width,0))



class Button:
    def __init__(self, text, x, y, scale = 3):
        original_image = pygame.image.load(BUTTON_IMG_PATH).convert_alpha()
        width = original_image.get_width() * scale
        height = original_image.get_height() * scale

        self.image = pygame.transform.scale(original_image, (width, height))
        self.rect = self.image.get_rect(center = (x, y))
        self.text = text
        self.font = pygame.font.SysFont("Arial", 20 * scale, bold=True)
        self.is_hovered = False


    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)


        color = GOLD if self.is_hovered else WHITE
        text_surf = self.font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center = self.rect.center)
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))

        surface.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text_surf, text_rect)

class Menu:
    def __init__(self):
        self.screen_obj = Screen()
        self.screen = self.screen_obj.get_display()
        self.running = True
        self.clock = pygame.time.Clock()

        self.background = ScrollingBackground(self.screen.get_height(), speed = 2)
        start_y = 250
        gap = 120                                             #Espace entre les boutons

        self.btn_play = Button("JOUER", center_x, start_y)
        self.btn_settings = Button("PARAMETRES", center_x, start_y + gap)
        self.btn_tuto = Button("TUTORIEL", center_x, start_y + gap * 2)

        self.buttons = [self.btn_play, self.btn_settings, self.btn_tuto]

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
                        return "Menu Tuto à faire"

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
            
            title_font = pygame.font.SysFont("Arial", 80, bold = True)
            title_surf = title_font.render("Laser Game", True, WHITE)

            self.screen.blit(shadow_surf, (self.screen.get_width() // 2 - title_surf.get_width() // 2 + 4, 84))
            self.screen.blit(title_surf, (self.screen.get_width() // 2 - title_surf.get_width() // 2, 80))

            for btn in self.buttons:
                btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)
