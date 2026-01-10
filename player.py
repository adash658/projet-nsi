import pygame
import main

pygame.init()
ecran = pygame.display.set_mode((700, 400))
black = (0, 0, 0)
white = (255, 255, 255)
ecran.fill(white)
img = pygame.image.load("placeholder.png").convert_alpha()
