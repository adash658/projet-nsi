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
        
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen, camera_x, camera_y):

        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))