import pygame

BACKGROUND_PATH = "Image/Image de fond.png"

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