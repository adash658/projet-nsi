import pygame as pg
from sources.constants import *
from sources.player import *
from sources.npc import NPC
from pytmx.util_pygame import load_pygame
from sources.tile import Tile, CollisionTile
from sources.database import Dialogue


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((LARGEUR, HAUTEUR))
        pg.display.set_caption("Glade")
        self.horloge = pg.time.Clock()
        self.play = True
        self.tmx_data = load_pygame("assets/map.tmx")
        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth * 2
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight * 2
        self.player = Player(self.map_width // 2, self.map_height // 2)
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.rect.center = (self.player.posix, self.player.posiy)
        self.font = pg.font.Font(arial, 20)
        self.txt_pause = self.font.render("Pause, appuyez sur Echap", True, NOIR)
        self.npcs = []
        self.current_dialogue = None
        self.current_player = None
        Luna = NPC("Luna", 200, 200, "assets/luna.png")
        self.npcs.append(Luna)
        self.sprite_group = pg.sprite.Group()
        self.collisions = pg.sprite.Group()
        self.camera_x = 0
        self.camera_y = 0
        self.intro_lines = [
            "12:34 - AN 56 - 07 AOUT",
            "",
            """59° 2?' ??" N, 18° 5?' ??" E""",
            "",
            ""
        ]
        self.in_intro = True
        self.intro_start_time = 0
        self.intro_duration = 5658

        self.map_surface = pg.Surface((self.map_width, self.map_height)).convert()
        self.render_map()
        self.starting = True
        for layer in self.tmx_data.layers:
            if layer.name == "collision":
                for obj in layer:
                    CollisionTile(
                        obj.x * 2,
                        obj.y * 2,
                        obj.width * 2,
                        obj.height * 2,
                        self.collisions,
                    )

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

                self.intro_start_time = pg.time.get_ticks()
                
            while self.in_intro and self.play:
                self.update_intro()

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
                            if self.current_dialogue:
                                self.current_dialogue = None
                                self.current_speaker = None
                            else:
                                phrase = Dialogue.dialogue(npc, ordre=1)
                                self.current_dialogue = phrase
                                self.current_speaker = npc
                        else:
                            self.current_dialogue = None
            if not self.player.ispaused:
                self.player.move(self.collisions)

            self.camera_x = self.player.posix - LARGEUR // 2
            self.camera_y = self.player.posiy - HAUTEUR // 2

            pg.draw.rect(
                self.screen,
                (255, 0, 0),
                (300 - self.camera_x, 300 - self.camera_y, 50, 50),
            )

            screen_x = self.player.posix - self.camera_x
            screen_y = self.player.posiy - self.camera_y
            self.screen.blit(self.player.image, (screen_x - 48, screen_y - 64))

            if self.player.ispaused:
                self.screen.blit(self.txt_pause, (10, 10))

            for pnj in self.npcs:
                pnj.draw(self.screen, self.camera_x, self.camera_y)

            self.draw_dialogue()

            pg.display.flip()
            self.horloge.tick(FPS)

        pg.quit()

    def update_intro(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.play = False
                self.in_intro = False

        current_time = pg.time.get_ticks()
        
        if current_time - self.intro_start_time > self.intro_duration:
            self.in_intro = False
            return

        self.screen.fill((0, 0, 0))
        
        hauteur_ligne = 40
        hauteur_totale = len(self.intro_lines) * hauteur_ligne
        start_y = (HAUTEUR - hauteur_totale) // 2 

        for i, phrase in enumerate(self.intro_lines):
            text_surf = self.font.render(phrase, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(LARGEUR // 2, start_y + i * hauteur_ligne))
            self.screen.blit(text_surf, text_rect)

        pg.display.flip()

    def render_map(self):
        scaled_cache = {}
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    if image not in scaled_cache:
                        scaled_cache[image] = pg.transform.scale_by(image, 2)
                    scaled_image = scaled_cache[image]
                    self.map_surface.blit(
                        scaled_image,
                        (x * self.tmx_data.tilewidth *2,
                        y * self.tmx_data.tileheight *2)
                    )

    def draw_dialogue(self):
        if self.current_dialogue:
            box_rect = pg.Rect(50, HAUTEUR - 150, LARGEUR - 100, 120)
            pg.draw.rect(self.screen, (0, 0, 0), box_rect)
            pg.draw.rect(self.screen, (255, 255, 255), box_rect, 5)
            
            nom_surface = self.font.render(self.current_speaker, True, (255, 255, 0))
            self.screen.blit(nom_surface, (box_rect.x + 20, box_rect.y + 10))

            texte_surface = self.font.render(self.current_dialogue, True, (255, 255, 255))
            self.screen.blit(texte_surface, (box_rect.x + 20, box_rect.y + 40))