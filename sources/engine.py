import pygame as pg
from sources.constants import *

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((LARGEUR,HAUTEUR))
        pg.display.set_caption("Glade")
        self.horloge = pg.time.Clock()
        self.play = True

    def run(self):

        while self.play:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.play = False

            self.screen.fill(BLANC)
            
            pg.display.flip()

            self.horloge.tick(FPS)

        pg.quit()