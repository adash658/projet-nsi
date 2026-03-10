import pygame as pg
from sources.constants import *
from sources.player import *
from sources.npc import NPC
from pytmx.util_pygame import load_pygame
from sources.tile import Tile, CollisionTile
from sources.database import Dialogue

def preparer_portrait(image_brute, hauteur_finale, epaisseur_bordure):

    largeur_origine, hauteur_origine = image_brute.get_size()
    cote_carre = min(largeur_origine, hauteur_origine)
    x_crop = (largeur_origine - cote_carre) // 2
    y_crop = (hauteur_origine - cote_carre) // 2
    rect_crop = pg.Rect(x_crop, y_crop, cote_carre, cote_carre)
    image_carree = image_brute.subsurface(rect_crop)
    portrait_final = pg.transform.smoothscale(image_carree, (hauteur_finale, hauteur_finale))
    pg.draw.rect(portrait_final, (0, 0, 0), portrait_final.get_rect(), epaisseur_bordure)
    return portrait_final

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((LARGEUR, HAUTEUR))
        pg.display.set_caption("Glade")
        self.horloge = pg.time.Clock()
        self.play = True
        self.tmx_data = load_pygame("assets/map.tmx")
        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth * 4
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight * 4
        self.player = Player(1500, 7500)
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.rect.center = (self.player.posix, self.player.posiy)
        self.font = pg.font.Font(CHEMIN_POLICE, 30)
        self.font_intro = pg.font.Font(POLICE_INTRO, 30)
        self.txt_pause = self.font.render("Pause, appuyez sur Echap", True, NOIR)
        self.current_dialogue = None
        self.current_player = None
        cx = self.map_width // 2
        cy = self.map_height // 2
        Luna = NPC("Luna", cx - 200, cy + 50, "assets/luna.png")
        Gatouz = NPC("Gatouz", cx + 200, cy - 50, "assets/gatouz.png")
        Wina = NPC("Wina", cx - 150, cy - 200, "assets/wina.png")
        Spensi = NPC("Spensi", cx + 250, cy + 150, "assets/spensi.png")
        Kiko = NPC("Kiko", cx, cy + 250, "assets/kiko.png")
        self.npcs = []
        self.npcs.extend([Luna, Gatouz, Wina, Spensi, Kiko])
        self.sprite_group = pg.sprite.Group()
        self.collisions = pg.sprite.Group()
        self.camera_x = 0
        self.camera_y = 0
        self.ecran_titre = pg.image.load("assets/Glade.png").convert()
        self.ecran_titre = pg.transform.scale(self.ecran_titre, (LARGEUR, HAUTEUR))
        image_play = pg.image.load("assets/Menu/Main Menu/Play_Not-Pressed.png").convert_alpha()
        image_play_pressed = pg.image.load("assets/Menu/Main Menu/Play_Pressed.png").convert_alpha()
        self.play_button = pg.transform.scale_by(image_play, 5)
        self.play_pressed_button = pg.transform.scale_by(image_play_pressed, 5)
        self.play_rect = self.play_button.get_rect(midbottom=(LARGEUR // 2, HAUTEUR - 30))
        self.button_pressed = False
        self.dialogue_pages = []
        self.current_page = 0

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
                        obj.x * 4,
                        obj.y * 4,
                        obj.width * 4,
                        obj.height * 4,
                        self.collisions,
                    )

    def run(self):
        while self.play:
            while self.starting:

                self.screen.blit(self.ecran_titre, (0, 0))
                
                if self.button_pressed:
                    self.screen.blit(self.play_pressed_button, self.play_rect)
                else:
                    self.screen.blit(self.play_button, self.play_rect)

                pg.display.flip()

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.play = False
                        self.starting = False
                    
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_RETURN:
                            self.starting = False
                            
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1 and self.play_rect.collidepoint(event.pos):
                            self.button_pressed = True
                            
                    elif event.type == pg.MOUSEBUTTONUP:
                        if event.button == 1 and self.button_pressed:
                            self.starting = False
                        self.button_pressed = False

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
                        if self.current_dialogue:
                            # 1. Le dialogue est ouvert : E permet de le quitter de force
                            self.current_dialogue = None
                            self.current_speaker_name = None
                            self.current_speaker_obj = None
                            self.current_emotion = None
                            self.dialogue_pages = []

                        else:
                            npc_name = self.player.check_interaction(self.npcs)
                            if npc_name:
                                if self.current_dialogue:
                                    self.current_dialogue = None
                                    self.current_speaker_name = None
                                    self.current_speaker_obj = None
                                    self.current_emotion = None
                                else:
                                    phrase, emotion = Dialogue.dialogue(npc_name, 1)
                                    self.current_dialogue = phrase
                                    self.current_speaker_name = npc_name
                                    self.current_emotion = emotion
                                    for pnj in self.npcs:
                                        if pnj.name == npc_name:
                                            self.current_speaker_obj = pnj
                                            break
                                    box_rect = pg.Rect(200, HAUTEUR - 250, LARGEUR - 400, 200)
                                    text_wrap_rect = pg.Rect(box_rect.x + 20, box_rect.y + 50, box_rect.width - 40, box_rect.height - 70)
                                    self.dialogue_pages = self.calculer_pages(phrase, text_wrap_rect, self.font, max_lignes=4)
                                    self.current_page = 0
                            else:
                                self.current_dialogue = None
                    if event.key == pg.K_RETURN:
                        if self.current_dialogue:
                            if self.current_page < len(self.dialogue_pages) - 1:
                                self.current_page += 1
                            else:
                                self.current_dialogue = None
                                self.current_speaker_name = None
                                self.current_speaker_obj = None
                                self.current_emotion = None
                                self.dialogue_pages = []

            if not self.player.ispaused:
                if self.current_dialogue:
                    self.player.state = "Idle"
                    self.player.animate()
                else:
                    self.player.move(self.collisions)

            self.camera_x = self.player.posix - LARGEUR // 2
            self.camera_y = self.player.posiy - HAUTEUR // 2

            player_rect_screen = self.player.rect.copy()
            player_rect_screen.x -= self.camera_x
            player_rect_screen.y -= self.camera_y
            player_image_rect = self.player.image.get_rect(center=player_rect_screen.center)
            self.screen.blit(self.player.image, player_image_rect)

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
            keys = pg.key.get_pressed()
            if keys[pg.K_a] and keys[pg.K_z] and keys[pg.K_e]:
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
            text_surf = self.font_intro.render(phrase, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(LARGEUR // 2, start_y + i * hauteur_ligne))
            self.screen.blit(text_surf, text_rect)

        pg.display.flip()

    def render_map(self):
        scaled_cache = {}
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    if image not in scaled_cache:
                        scaled_cache[image] = pg.transform.scale_by(image, 4)
                    scaled_image = scaled_cache[image]
                    self.map_surface.blit(
                        scaled_image,
                        (x * self.tmx_data.tilewidth *4,
                        y * self.tmx_data.tileheight *4)
                    )

    def draw_dialogue(self):
        if self.current_dialogue:
            box_rect = pg.Rect(200, HAUTEUR - 250, LARGEUR - 400, 200)
            pg.draw.rect(self.screen, (0, 0, 0), box_rect)
            pg.draw.rect(self.screen, (255, 255, 255), box_rect, 5)

            if self.current_emotion and self.current_speaker_obj and self.current_emotion in self.current_speaker_obj.portraits:
                image_brute = self.current_speaker_obj.portraits[self.current_emotion]
                portrait = preparer_portrait(image_brute, 256, 10)
                self.screen.blit(portrait, (box_rect.x, box_rect.y - 256))

            couleur_nom = COULEURS_PNJ.get(self.current_speaker_name, (255, 255, 0))
            nom_surface = self.font.render(self.current_speaker_name, True, couleur_nom)
            self.screen.blit(nom_surface, (box_rect.x + 20, box_rect.y + 10))

            text_wrap_rect = pg.Rect(box_rect.x + 20, box_rect.y + 50, box_rect.width - 40, box_rect.height - 70)

            if hasattr(self, 'dialogue_pages') and self.dialogue_pages:
                lignes_a_afficher = self.dialogue_pages[self.current_page]
                
                for i, ligne in enumerate(lignes_a_afficher):
                    texte_surface = self.font.render(ligne, True, (255, 255, 255))
                    self.screen.blit(texte_surface, (text_wrap_rect.x, text_wrap_rect.y + (i * 35)))
                
                if self.current_page < len(self.dialogue_pages) - 1:
                    triangle_surf = self.font_intro.render("▼", True, (255, 255, 0))
                    self.screen.blit(triangle_surf, (box_rect.right - 30, box_rect.bottom - 40))

    def calculer_pages(self, text, rect, font, max_lignes=4):
        mots = text.split(' ')
        lignes = []
        ligne_en_cours = ""
        
        for mot in mots:
            test_ligne = ligne_en_cours + mot + " "
            if font.size(test_ligne)[0] < rect.width:
                ligne_en_cours = test_ligne
            else:
                lignes.append(ligne_en_cours)
                ligne_en_cours = mot + " "
        lignes.append(ligne_en_cours)
        
        pages = []
        for i in range(0, len(lignes), max_lignes):
            pages.append(lignes[i:i + max_lignes])
            
        return pages