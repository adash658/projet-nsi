import pygame as pg
from sources.constants import *
from sources.player import *
from sources.npc import NPC
from pytmx.util_pygame import load_pygame
from sources.Tile import Tile


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((LARGEUR, HAUTEUR))
        pg.display.set_caption("Glade")
        self.horloge = pg.time.Clock()
        self.play = True
        self.player = Player(0, 0)
        self.font = pg.font.Font(arial, 20)
        self.txt_pause = self.font.render("Pause, appuyez sur Echap", True, NOIR)
        self.npcs = []
        luna = NPC("luna", 200, 200)
        self.npcs.append(luna)
        self.tmx_data = load_pygame("assets/map.tmx")
        self.sprite_group = pg.sprite.Group()
        self.camera_x = 0
        self.camera_y = 0
        for layer in self.tmx_data.layers:
            if hasattr(layer, "data"):
                for x, y, surf in layer.tiles():
                    pos = (
                        x * self.tmx_data.tilewidth,
                        y * self.tmx_data.tileheight,
                    )
                    Tile(pos=pos, image=surf, groups=self.sprite_group)

    def run(self):
        while self.play:

            self.screen.fill(BLANC)
            for sprite in self.sprite_group:
                # Calculer la position à l’écran par rapport à la caméra
                screen_pos = (
                    sprite.rect.x - self.camera_x,
                    sprite.rect.y - self.camera_y,
                )
                # Dessiner la tuile à cette position
                self.screen.blit(sprite.image, screen_pos)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.play = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:

                        if self.player.ispaused == False:
                            self.player.lock()
                        else:
                            self.player.unlock()

                    if event.key == pg.K_e:
                        npc = self.player.check_interaction(self.npcs)
                        if npc:
                            print(f"Tu parles à {npc}")

            if not self.player.ispaused:
                self.player.move()

            self.camera_x = self.player.posix - LARGEUR // 2
            self.camera_y = self.player.posiy - HAUTEUR // 2

            pg.draw.rect(
                self.screen,
                (255, 0, 0),
                (300 - self.camera_x, 300 - self.camera_y, 50, 50),
            )

            screen_x = self.player.posix - self.camera_x
            screen_y = self.player.posiy - self.camera_y
            self.screen.blit(self.player.image, (screen_x - 24, screen_y - 32))

            if self.player.ispaused:
                self.screen.blit(self.txt_pause, (10, 10))

            for pnj in self.npcs:
                pnj.draw(self.screen, self.camera_x, self.camera_y)

            pg.display.flip()
            self.horloge.tick(FPS)

        pg.quit()
