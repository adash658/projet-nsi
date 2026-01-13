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
        self.player = Player(100, 100, 2, False)

    def run(self):
        while self.play:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.play = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self.player.ispaused == False:
                            self.player.lock()
                        else:
                            self.player.unlock()
            self.player.move()
            self.screen.fill(BLANC)
            self.screen.blit(self.player.image, (self.player.posix, self.player.posiy))
            if self.player.ispaused:
                self.screen.blit(
                    pg.font.Font(cst.arial, 20).render(
                        "Pause, appuyez sur Echap pour continuer", True, NOIR
                    ),
                    (0, 0),
                )

            pg.display.flip()

            self.horloge.tick(FPS)

        pg.quit()
