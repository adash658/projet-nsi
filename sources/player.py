import pygame as pg
import engine
import constants as cst

pygame.init()
class Player(self,x,y):
    def __init__(self,x,y):
        self.image = cst.Player_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def move(self):
        for event in pygame.event.get():
            if event.key == pygame.K_LEFT:
                self.rect.move_ip(-2,0)
            if event.key == pygame.K_RIGHT:
                self.rect.move_ip(2,0)
            if event.key == pygame.K_UP:
                self.rect.move_ip(0,-2)
            if event.key == pygame.K_DOWN:
                self.rect.move_ip(0,2)
    