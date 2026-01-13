import pygame 
from sources.engine import *
import sources.constants as cst

pygame.init()
class Player:
    def __init__(self,x,y):
        self.image = cst.Player_img
        self.rect = self.image.get_rect()
        self.posix = x
        self.posiy = y 
        self.speed = 2
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
    