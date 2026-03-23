import pygame as pg


class Tile(pg.sprite.Sprite):
    def __init__(self, pos, image, groups):
        super().__init__(groups)
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
class CollisionTile(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, groups):
        super().__init__(groups)
        self.rect = pg.Rect(x, y, width, height)
class PolygonCollisionTile(pg.sprite.Sprite):
    def __init__(self, points_absolus, group):
        super().__init__(group)
        # Bounding box (pour le broad-phase, collision rapide)
        xs = [p[0] for p in points_absolus]
        ys = [p[1] for p in points_absolus]
        self.rect = pg.Rect(min(xs), min(ys),
                                max(xs) - min(xs),
                                max(ys) - min(ys))
        # Points exacts du polygone (pour la précision)
        self.points = points_absolus