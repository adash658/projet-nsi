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
        self.player = Player(0, 0)
        self.font = pg.font.Font(arial, 20)
        self.txt_pause = self.font.render("Pause, appuyez sur Echap", True, NOIR)

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

            if not self.player.ispaused:
                self.player.move()

            self.camera_x = self.player.posix - LARGEUR // 2
            self.camera_y = self.player.posiy - HAUTEUR // 2

            self.screen.fill(BLANC)

            pg.draw.rect(self.screen, (255, 0, 0), (300 - self.camera_x, 300 - self.camera_y, 50, 50))
            
            screen_x = self.player.posix - self.camera_x
            screen_y = self.player.posiy - self.camera_y
            self.screen.blit(self.player.image, (screen_x - 24, screen_y - 32))
            
            if self.player.ispaused:
                self.screen.blit(self.txt_pause, (10, 10))

            pg.display.flip()
            self.horloge.tick(FPS)
        pg.quit()
