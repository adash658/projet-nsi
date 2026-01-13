import pygame as pg
from sources.constants import *
from sources.player import *


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((LARGEUR, HAUTEUR))
        pg.display.set_caption("Glade")
        self.horloge = pg.time.Clock()
        self.play = True
        self.player = Player(400, 300)

    def run(self):

        while self.play:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.play = False
            self.player.move()
            self.screen.fill(BLANC)
            self.screen.blit(self.player.image, (self.player.posix, self.player.posiy))

            pg.display.flip()

            self.horloge.tick(FPS)

        pg.quit()
