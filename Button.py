import pygame

# On définit les constantes ici pour qu'elles soient accessibles
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
BUTTON_IMG_PATH = "Sprites/ATH/spr_banner_hud.png"

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