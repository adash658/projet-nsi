import pygame
import sources.constants as cst

class Player:
    def __init__(self, x, y, speed=2, ispaused=False):
        self.image = cst.Player_img
        self.rect = self.image.get_rect()
        self.posix = x
        self.posiy = y
        self.speed = speed
        self.ispaused = ispaused

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.posix -= self.speed
        if keys[pygame.K_RIGHT]:
            self.posix += self.speed
        if keys[pygame.K_UP]:
            self.posiy -= self.speed
        if keys[pygame.K_DOWN]:
            self.posiy += self.speed
        self.rect.topleft = (self.posix, self.posiy)

    def lock(self):
        self.speed = 0
        self.ispaused = True

    def unlock(self):
        self.speed = 2
        self.ispaused = False
