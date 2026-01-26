import pygame as pg
from sources.constants import *
from sources.player import *
from sources.npc import NPC
from pytmx.util_pygame import load_pygame
from sources.Tile import Tile
from sources.database import Dialogue

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
        self.current_dialogue = None
        luna = NPC("luna", 200, 200) 
        self.npcs.append(luna)
        self.tmx_data = load_pygame("assets/map.tmx")
        self.sprite_group = pg.sprite.Group()
        self.camera_x = 0
        self.camera_y = 0
        map_width = self.tmx_data.width * self.tmx_data.tilewidth
        map_height = self.tmx_data.height * self.tmx_data.tileheight
        self.map_surface = pg.Surface((map_width, map_height)).convert()
        self.render_map()
        self.starting = True

    def run(self):
        while self.play:
            while self.starting:
                self.screen.fill(BLANC)
                txt_start = self.font.render("Appuyez sur une touche pour commencer", True, NOIR)
                pg.draw.rect(
                    self.screen,
                    (0, 0, 255),
                    (LARGEUR // 2 - 150, HAUTEUR // 2 - 30, 300, 60)
                    )

                self.screen.blit(txt_start, (LARGEUR // 2 - txt_start.get_width() // 2, HAUTEUR // 2))
                pg.display.flip()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.play = False
                        self.starting = False
                    if event.type == pg.KEYDOWN:
                        self.starting = False
                button_rect = pg.Rect(
                        LARGEUR // 2 - 150,
                        HAUTEUR // 2 - 30,
                        300,
                        60
                    )
                if button_rect.collidepoint(pg.mouse.get_pos()):
                    self.starting = False

            self.screen.fill(BLANC)
            self.screen.blit(
                self.map_surface,
                (-self.camera_x, -self.camera_y)
                )
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
                            phrase = Dialogue.dialogue(npc, ordre=1)
                            self.current_dialogue = phrase
                            print(f"{npc} : {phrase}")

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
    def render_map(self):
            for layer in self.tmx_data.visible_layers:
                if hasattr(layer, "tiles"):
                    for x, y, image in layer.tiles():
                        self.map_surface.blit(
                            image,
                            (x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight)
                        )