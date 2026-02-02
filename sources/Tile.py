import pygame as pg


class Tile(pg.sprite.Sprite):
    def __init__(self, pos, image, groups):
        super().__init__(groups)
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
class CollisionTile(pg.sprite.Sprite):
    def __init__(self, x, y, size, groups):
        super().__init__(groups)
        self.rect = pg.Rect(x, y, size, size)