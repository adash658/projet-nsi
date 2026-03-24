import pygame as pg
from sources.constants import *
from sources.player import *
from sources.npc import NPC
from pytmx.util_pygame import load_pygame
from sources.Tile import Tile, CollisionTile, PolygonCollisionTile
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
        
        self.etat_jeu = ETAT_MENU

        self.etape_histoire = 1 
        
        self.tmx_data = load_pygame("assets/map.tmx")
        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth * 4
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight * 4
        self.map_surface = pg.Surface((self.map_width, self.map_height)).convert()
        self.render_map()
        
        self.collisions = pg.sprite.Group()
        for layer in self.tmx_data.layers:
            if layer.name == "collision":
                for obj in layer:
                    if hasattr(obj, 'points') and obj.points:
                        points_absolus = [(p[0] * 4, p[1] * 4) for p in obj.points]
                        PolygonCollisionTile(points_absolus, self.collisions)
                    else:
                        CollisionTile(obj.x * 4, obj.y * 4, obj.width * 4, obj.height * 4, self.collisions)
                        
        self.player = Player(1167, 4404)
        self.player.direction = "right"
        self.player.state = "Idle"
        self.player.image = self.player.animations["Idle"]["right"][0]
        self.rect = pg.Rect(0, 0, 32, 32)
        self.rect.center = (self.player.posix, self.player.posiy)
        
        Luna = NPC("Luna", 1250, 4404, "IL")
        Gatouz = NPC("Gatouz", 0, 0)
        Wina = NPC("Wina", 0, 0)
        Spensi = NPC("Spensi", 0, 0)
        Kiko = NPC("Kiko", 0, 0)
        self.npcs = [Luna, Gatouz, Wina, Spensi, Kiko]
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.font = pg.font.Font(CHEMIN_POLICE, 30)
        self.font_intro = pg.font.Font(POLICE_INTRO, 30)
        self.txt_pause = self.font.render("Pause, appuyez sur Echap", True, NOIR)
        
        self.ecran_titre = pg.transform.scale(pg.image.load("assets/Glade.png").convert(), (LARGEUR, HAUTEUR))
        self.play_button = pg.transform.scale_by(pg.image.load("assets/Menu/Main Menu/Play_Not-Pressed.png").convert_alpha(), 5)
        self.play_pressed_button = pg.transform.scale_by(pg.image.load("assets/Menu/Main Menu/Play_Pressed.png").convert_alpha(), 5)
        self.play_rect = self.play_button.get_rect(midbottom=(LARGEUR // 2, HAUTEUR - 30))
        self.button_pressed = False
        
        self.intro_lines = ["12:34 - AN 56 - 07 AOUT", "", """59° 2?' ??" N, 18° 5?' ??" E""", "", ""]
        self.intro_start_time = 0
        self.intro_duration = 5658
        
        self.current_dialogue_data = None  
        self.current_speaker_name = None
        self.current_speaker_obj = None
        self.current_emotion = None
        self.dialogue_pages = []
        self.current_page = 0
        self.en_attente_choix = False
        
        self.scene_actuelle = "A" 
        self.zone_clairiere = None
        self.zone_plage = pg.Rect(5849, 3744, 100, 100) # La zone pour lancer la scène C
              
        self.fondu_alpha = 255
        self.fondu_surface = pg.Surface((LARGEUR, HAUTEUR))
        self.fondu_surface.fill((0, 0, 0))
        self.fondu_sens = -1 
        self.fondu_duree = 1500
        self.fondu_start = None

    def run(self):
        while self.play:
            self.horloge.tick(FPS)
            self.gerer_evenements()
            self.mettre_a_jour()
            self.dessiner()
        pg.quit()

    def gerer_evenements(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.play = False

            if self.etat_jeu == ETAT_MENU:
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.etat_jeu = ETAT_INTRO
                    self.intro_start_time = pg.time.get_ticks()
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.play_rect.collidepoint(event.pos):
                    self.button_pressed = True
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.button_pressed:
                    self.etat_jeu = ETAT_INTRO
                    self.intro_start_time = pg.time.get_ticks()
                    self.button_pressed = False

            elif self.etat_jeu == ETAT_INTRO:
                keys = pg.key.get_pressed()
                if keys[pg.K_a] and keys[pg.K_z] and keys[pg.K_e]:
                    self.etat_jeu = ETAT_JEU
                    self.fondu_duree = 3658
                    self.fondu_start = pg.time.get_ticks()

            elif self.etat_jeu == ETAT_JEU:
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        vrai_x = mouse_x + self.camera_x
                        vrai_y = mouse_y + self.camera_y
                        print(f"Curseur Map : x={vrai_x}, y={vrai_y}")
                if event.type == pg.KEYDOWN:
                    keys = pg.key.get_pressed()
                    if keys[pg.K_a] and keys[pg.K_z] and keys[pg.K_e] and self.etape_histoire == 1:
                        self.etat_jeu = ETAT_CINEMATIQUE
                        self.scene_actuelle = "TRANS_A_B"
                        self.fondu_sens = 1
                        self.fondu_start = pg.time.get_ticks()
                        self.fondu_duree = 1500
                        self.player.state = "Idle"
                        print("Debug : Skip vers la Clairière (Scène 2)")
                    elif event.key == pg.K_ESCAPE:
                        self.etat_jeu = ETAT_PAUSE
                    elif event.key == pg.K_p:
                        print(f"Position Joueur : x={self.player.rect.centerx}, y={self.player.rect.centery}")
                    elif event.key in (pg.K_e, pg.K_RETURN): 
                        npc_name = self.player.check_interaction(self.npcs)
                        if npc_name:
                            pnj_cible = next((p for p in self.npcs if p.name == npc_name), None)
                            if pnj_cible and not pnj_cible.chemin:
                                dx = self.player.posix - pnj_cible.rect.centerx
                                dy = self.player.posiy - pnj_cible.rect.centery
                                
                                if abs(dx) > abs(dy):
                                    etat_voulu = "IR" if dx > 0 else "IL"
                                else:
                                    etat_voulu = "ID" if dy > 0 else "IU"
                                
                                interaction_autorisee = False
                                
                                if len(pnj_cible.animations.get(etat_voulu, [])) > 0:
                                    pnj_cible.state = etat_voulu
                                    pnj_cible.current_frame = 0
                                    pnj_cible.image = pnj_cible.animations[etat_voulu][0]
                                    interaction_autorisee = True
                                else:
                                    if pnj_cible.state[-1] == etat_voulu[-1]:
                                        interaction_autorisee = True
                                
                                if interaction_autorisee:
                                    self.current_speaker_name = npc_name
                                    self.current_speaker_obj = pnj_cible
                                    data = Dialogue.get_premier(npc_name, self.etape_histoire)
                                    if data:
                                        self.charger_dialogue(data)
                                        self.etat_jeu = ETAT_DIALOGUE
                                        
            elif self.etat_jeu == ETAT_DIALOGUE:
                if event.type == pg.KEYDOWN:
                    if event.key in (pg.K_e, pg.K_RETURN):
                        if not self.en_attente_choix:
                            if self.current_page < len(self.dialogue_pages) - 1:
                                self.current_page += 1
                            else:
                                _id, speaker, event_str, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z = self.current_dialogue_data
                                if choix_a and choix_z:
                                    self.en_attente_choix = True
                                elif next_id:
                                    self.charger_dialogue(Dialogue.get_par_id(next_id))
                                else:
                                    etat_prochain = ETAT_JEU 
                                    
                                    if event_str is not None:
                                        event_id = int(event_str)
                                        if event_id == 1: 
                                            luna = next((p for p in self.npcs if p.name == "Luna"), None)
                                            if luna:
                                                chemin_luna = [(3814, 4404), (3814, 3340), (4810, 3340), (4810, 2965), (5500, 2965), (5500, 2750), (5728, 2750)]
                                                luna.donner_chemin(chemin_luna)
                                                
                                        elif event_id == 2:
                                            self.scene_actuelle = "C"
                                            
                                        elif event_id == 3:
                                            etat_prochain = ETAT_CINEMATIQUE 
                                            self.scene_actuelle = "TRANS_B_FREE"
                                            self.fondu_sens = 1
                                            self.fondu_start = pg.time.get_ticks()
                                            self.fondu_duree = 1500
                                            
                                    self.fermer_dialogue()
                                    self.etat_jeu = etat_prochain

                    elif event.key == pg.K_a and self.en_attente_choix:
                        _id, speaker, event_str, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z = self.current_dialogue_data
                        if next_id_a:
                            self.charger_dialogue(Dialogue.get_par_id(next_id_a))
                        else:
                            self.fermer_dialogue()
                            self.etat_jeu = ETAT_JEU

                    elif event.key == pg.K_z and self.en_attente_choix:
                        _id, speaker, event_str, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z = self.current_dialogue_data
                        if next_id_z:
                            self.charger_dialogue(Dialogue.get_par_id(next_id_z))
                        else:
                            self.fermer_dialogue()
                            self.etat_jeu = ETAT_JEU

            elif self.etat_jeu == ETAT_PAUSE:
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.etat_jeu = ETAT_JEU


    def mettre_a_jour(self):
        self.verifier_declencheurs_histoire()

        if self.etat_jeu == ETAT_INTRO:
            if pg.time.get_ticks() - self.intro_start_time > self.intro_duration:
                self.etat_jeu = ETAT_JEU
                self.fondu_start = pg.time.get_ticks()

        elif self.etat_jeu in (ETAT_JEU, ETAT_CINEMATIQUE):
            for pnj in self.npcs:
                if pnj.chemin:
                    pnj.suivre_chemin()
                pnj.animate()

            if self.etat_jeu == ETAT_JEU:
                obstacles = list(self.collisions) + [pnj.rect for pnj in self.npcs]
                self.player.move(obstacles)
            
            self.camera_x = self.player.posix - LARGEUR // 2
            self.camera_y = self.player.visual_center_y - HAUTEUR // 2

        if self.etat_jeu == ETAT_CINEMATIQUE:
            self.jouer_scene()

    def jouer_scene(self):
        progression = 0
        if self.fondu_start is not None:
            progression = min(1.0, (pg.time.get_ticks() - self.fondu_start) / self.fondu_duree)

        if self.scene_actuelle == "CLAIRIERE":
            if self.fondu_sens == 1: 
                self.fondu_alpha = int(progression * 255)
                if progression >= 1.0:
                    luna = next((p for p in self.npcs if p.name == "Luna"), None)
                    cx, cy = luna.rect.x + 150, luna.rect.y
                    for p in self.npcs:
                        if p.name == "Gatouz": p.rect.midbottom = (cx, cy - 100)
                        elif p.name == "Wina": p.rect.midbottom = (cx + 100, cy - 40)
                        elif p.name == "Spensi": p.rect.midbottom = (cx + 80, cy + 80)
                        elif p.name == "Kiko": p.rect.midbottom = (cx - 100, cy - 40)
                    
                    self.player.rect.midbottom = (cx - 80, cy + 80)
                    self.player.posix, self.player.posiy = self.player.rect.center
                    self.player.direction = "right"
                    self.player.animate()
                    
                    self.etape_histoire = 2
                    self.current_speaker_name = "Gatouz"
                    self.current_speaker_obj = next((p for p in self.npcs if p.name == "Gatouz"), None)
                    
                    data = Dialogue.get_premier("Gatouz", self.etape_histoire) 
                    if data:
                        self.charger_dialogue(data)
                    
                    self.fondu_sens = -1
                    self.fondu_start = pg.time.get_ticks()
                    
            elif self.fondu_sens == -1:
                self.fondu_alpha = max(0, 255 - int(progression * 255))
                if progression >= 1.0:
                    self.fondu_start = None
                    self.scene_actuelle = None
                    self.etat_jeu = ETAT_DIALOGUE

        elif self.scene_actuelle == "TRANS_A_B":
            if self.fondu_sens == 1:
                self.fondu_alpha = int(progression * 255)
                if progression >= 1.0:
                    self.player.rect.midbottom = (5695, 2920)
                    self.player.posix, self.player.posiy = 5695, 2920

                    for p in self.npcs:
                        if p.name == "Luna": p.rect.midbottom = (5715, 2808)
                        elif p.name == "Gatouz": p.rect.midbottom = (5799, 2694)
                        elif p.name == "Spensi": p.rect.midbottom = (5960, 2718)
                        elif p.name == "Wina": p.rect.midbottom = (6035, 2822)
                        elif p.name == "Kiko": p.rect.midbottom = (6047, 2914)
                        kiko = next((p for p in self.npcs if p.name == "Kiko"), None)
                        wina = next((p for p in self.npcs if p.name == "Wina"), None)
                        if kiko: kiko.state = "IL"; kiko.current_frame = 0; kiko.image = kiko.animations["IL"][0]
                        if wina: wina.state = "IL"; wina.current_frame = 0; wina.image = wina.animations["IL"][0]

                    data = Dialogue.get_premier("Gatouz", 2)
                    if data:
                        self.charger_dialogue(data)

                    self.fondu_sens = -1
                    self.fondu_start = pg.time.get_ticks()

            elif self.fondu_sens == -1:
                self.fondu_alpha = max(0, 255 - int(progression * 255))
                if progression >= 1.0:
                    self.fondu_start = None
                    self.scene_actuelle = "B"
                    self.etat_jeu = ETAT_DIALOGUE

        elif self.scene_actuelle == "TRANS_B_C":
            if self.fondu_sens == 1:
                self.fondu_alpha = int(progression * 255)
                if progression >= 1.0:
                    self.player.rect.midbottom = (6300, 8802)
                    self.player.posix, self.player.posiy = 6300, 8802

                    gatouz = next((p for p in self.npcs if p.name == "Gatouz"), None)
                    if gatouz:
                        gatouz.rect.midbottom = (6407, 8802)

                    data = Dialogue.get_premier("Gatouz", 3)
                    if data:
                        self.charger_dialogue(data)

                    self.fondu_sens = -1
                    self.fondu_start = pg.time.get_ticks()

            elif self.fondu_sens == -1:
                self.fondu_alpha = max(0, 255 - int(progression * 255))
                if progression >= 1.0:
                    self.fondu_start = None
                    self.scene_actuelle = "C"
                    self.etat_jeu = ETAT_DIALOGUE
        elif self.scene_actuelle == "TRANS_B_FREE":
            if self.fondu_sens == 1:
                self.fondu_alpha = int(progression * 255)
                if progression >= 1.0:
                    gatouz = next((p for p in self.npcs if p.name == "Gatouz"), None)
                    if gatouz:
                        gatouz.rect.midbottom = (5849, 3744)
                    
                    self.etape_histoire = 3                    
                    self.fondu_sens = -1
                    self.fondu_start = pg.time.get_ticks()

            elif self.fondu_sens == -1:
                self.fondu_alpha = max(0, 255 - int(progression * 255))
                if progression >= 1.0:
                    self.fondu_start = None
                    self.scene_actuelle = "B_FREE"
                    self.etat_jeu = ETAT_JEU

    def dessiner(self):
        if self.etat_jeu == ETAT_MENU:
            self.screen.blit(self.ecran_titre, (0, 0))
            if self.button_pressed:
                self.screen.blit(self.play_pressed_button, self.play_rect)
            else:
                self.screen.blit(self.play_button, self.play_rect)

        elif self.etat_jeu == ETAT_INTRO:
            self.screen.fill((0, 0, 0))
            hauteur_ligne = 40
            start_y = (HAUTEUR - len(self.intro_lines) * hauteur_ligne) // 2 
            for i, phrase in enumerate(self.intro_lines):
                text_surf = self.font_intro.render(phrase, True, (255, 255, 255))
                self.screen.blit(text_surf, text_surf.get_rect(center=(LARGEUR // 2, start_y + i * hauteur_ligne)))

        elif self.etat_jeu in (ETAT_JEU, ETAT_DIALOGUE, ETAT_CINEMATIQUE, ETAT_PAUSE):
            self.screen.fill(BLANC)
            self.screen.blit(self.map_surface, (-self.camera_x, -self.camera_y))
            
            entites_a_dessiner = self.npcs + [self.player]
            entites_a_dessiner.sort(key=lambda entite: entite.rect.bottom)
            for entite in entites_a_dessiner:
                entite.draw(self.screen, self.camera_x, self.camera_y)

            if self.etat_jeu == ETAT_PAUSE:
                self.screen.blit(self.txt_pause, (10, 10))

            if self.etat_jeu == ETAT_DIALOGUE:
                self.draw_dialogue()

            if self.fondu_alpha > 0 and self.fondu_start is not None:
                if self.etat_jeu == ETAT_JEU and self.fondu_sens == -1:
                    elapsed = pg.time.get_ticks() - self.fondu_start
                    self.fondu_alpha = max(0, 255 - int((elapsed / self.fondu_duree) * 255))
                self.fondu_surface.set_alpha(self.fondu_alpha)
                self.screen.blit(self.fondu_surface, (0, 0))

        pg.display.flip()

    def render_map(self):
        scaled_cache = {}
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    if image not in scaled_cache:
                        scaled_cache[image] = pg.transform.scale_by(image,4)
                    scaled_image = scaled_cache[image]
                    self.map_surface.blit(
                        scaled_image,
                        (x * self.tmx_data.tilewidth *4,
                        y * self.tmx_data.tileheight *4)
                    )

    def draw_dialogue(self):
        if not self.current_dialogue_data:
            return

        _id, speaker, event, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z = self.current_dialogue_data

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

        if self.en_attente_choix:
            surf_a = self.font.render(f"[A]  {choix_a}", True, (173,200,222))
            surf_z = self.font.render(f"[Z]  {choix_z}", True, (180, 220, 255))
            self.screen.blit(surf_a, (text_wrap_rect.x, text_wrap_rect.y))
            self.screen.blit(surf_z, (text_wrap_rect.x, text_wrap_rect.y + 45))
        elif self.dialogue_pages:
            for i, ligne in enumerate(self.dialogue_pages[self.current_page]):
                texte_surface = self.font.render(ligne, True, (255, 255, 255))
                self.screen.blit(texte_surface, (text_wrap_rect.x, text_wrap_rect.y + (i * 35)))
            if self.current_page < len(self.dialogue_pages) - 1:
                triangle_surf = self.font_intro.render("▼", True, (255, 255, 0))
                self.screen.blit(triangle_surf, (box_rect.right - 30, box_rect.bottom - 40))
            elif not (choix_a and choix_z):
                triangle_surf = self.font_intro.render("▶", True, (200, 200, 200))
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

    def charger_dialogue(self, data):
        if data is None:
            self.fermer_dialogue()
            return

        _id, speaker, event, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z = data
        
        self.current_dialogue_data = data
        self.current_speaker_name = speaker
        self.current_emotion = emotion

        self.current_speaker_obj = next((p for p in self.npcs if p.name == speaker), None)
        
        box_rect = pg.Rect(200, HAUTEUR - 250, LARGEUR - 400, 200)
        text_wrap_rect = pg.Rect(box_rect.x + 20, box_rect.y + 50, box_rect.width - 40, box_rect.height - 70)
        self.dialogue_pages = self.calculer_pages(txt, text_wrap_rect, self.font, max_lignes=4)
        self.current_page = 0
        self.en_attente_choix = False

    def fermer_dialogue(self):
        self.current_dialogue_data = None
        self.current_speaker_name = None
        self.current_speaker_obj = None
        self.current_emotion = None
        self.dialogue_pages = []
        self.current_page = 0
        self.en_attente_choix = False
        self.player.unlock()

    def verifier_declencheurs_histoire(self):
        if self.etat_jeu != ETAT_JEU:
            return

        if self.scene_actuelle == "A":
            luna = next((p for p in self.npcs if p.name == "Luna"), None)
            if luna and not luna.chemin and luna.rect.x > 5700:
                dist_x = abs(self.player.posix - luna.rect.centerx)
                dist_y = abs(self.player.posiy - luna.rect.centery)
                
                if dist_x < 313 or dist_y < 251 :
                    self.etat_jeu = ETAT_CINEMATIQUE
                    self.scene_actuelle = "TRANS_A_B"
                    self.fondu_sens = 1
                    self.fondu_start = pg.time.get_ticks()
                    self.fondu_duree = 1500
                    self.player.state = "Idle"

        elif self.scene_actuelle == "B" and self.zone_plage:
            if self.player.rect.colliderect(self.zone_plage):
                self.etat_jeu = ETAT_CINEMATIQUE
                self.scene_actuelle = "TRANS_B_C"
                self.fondu_sens = 1
                self.fondu_start = pg.time.get_ticks()
                self.fondu_duree = 1500
                self.player.state = "Idle"