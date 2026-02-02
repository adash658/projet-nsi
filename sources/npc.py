import pygame
from sources.constants import *

class NPC:
    def __init__(self, name, x, y, image_path=None):
        self.name = name

        if image_path is None:
            self.image = placeholder.convert_alpha()
        else:
            self.image = pygame.image.load(image_path).convert_alpha()

        self.image = pygame.transform.scale_by(self.image, 2)

        self.rect = pygame.Rect(0, 0, 32, 16) 
        self.rect.center = (x, y)

    def draw(self, screen, camera_x, camera_y):
        image_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, (image_rect.x - camera_x, image_rect.y - camera_y))