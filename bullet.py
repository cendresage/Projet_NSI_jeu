import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, img):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pygame.math.Vector2(x, y)
        self.direction = direction.normalize()
        self.speed = speed
        self.image = img
        
        self.rotation = self.direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, self.rotation)
        
        # Configuration du rect et de la hitbox (pour la collision)
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        self.hitbox = self.rect.copy().inflate(-4, -4)


    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (self.pos.x, self.pos.y)
        self.hitbox.center = (self.pos.x, self.pos.y)