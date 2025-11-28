import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, img):
        pygame.sprite.Sprite.__init__(self)
        self.pos = x, y
        self.direction = pygame.math.Vector2(direction)
        self.speed = speed
        self.image = img
        
        self.rotation = self.direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, self.rotation)
        self.rect = self.image.get_rect()


def update(self):
    self.pos = (self.pos[0] + self.speed*self.direction[0], self.pos[1] + self.speed*self.direction[1])
    self.rect.center = self.pos