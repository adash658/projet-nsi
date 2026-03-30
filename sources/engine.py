import pygame as pg
from sources.constants import *
from sources.player import *
from sources.npc import NPC
from pytmx.util_pygame import load_pygame
from sources.Tile import Tile, CollisionTile, PolygonCollisionTile
from sources.database import Dialogue
from random import choice , randint

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

        self.font_pause = pg.font.Font(CHEMIN_POLICE, 100)
        self.txt_pause_grand = self.font_pause.render("PAUSE", True, (255, 255, 255))

        self.ecran_titre = pg.transform.scale(pg.image.load("assets/Glade.png").convert(), (LARGEUR, HAUTEUR))
        self.play_button = pg.transform.scale_by(pg.image.load("assets/Menu/Main Menu/Play_Not-Pressed.png").convert_alpha(), 5)
        self.play_pressed_button = pg.transform.scale_by(pg.image.load("assets/Menu/Main Menu/Play_Pressed.png").convert_alpha(), 5)
        self.play_rect = self.play_button.get_rect(midbottom=(LARGEUR // 2, HAUTEUR - 30))
        self.button_pressed = False

        self.intro_lines = ["12:34 - AN 56 - 07 AOUT", "", """59° 2?' ??" N, 18° 5?' ??" E""", "", "Day One"]
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

        self.bois_actif = False
        self.bois_image = pg.transform.scale_by(
            pg.image.load("assets/bois.png").convert_alpha(), 4)
        self.bois_rect  = self.bois_image.get_rect(center=(7007, 1786))
        self.zone_bois  = self.bois_rect.inflate(32, 32)
              
        self.fondu_alpha = 255
        self.fondu_surface = pg.Surface((LARGEUR, HAUTEUR))
        self.fondu_surface.fill((0, 0, 0))
        self.fondu_sens = -1 
        self.fondu_duree = 1500
        self.fondu_start = None

        self.soir_overlay = pg.Surface((LARGEUR, HAUTEUR))
        self.soir_overlay.fill((10, 10, 40))
        self.soir_start_time = None

        self.fin_lines = ["Day 1", "", "La nuit tombe sur l'île.", "", "End of Chapter 1","To be continued"]
        self.fin_start_time = 0
        self.fin_fondu_start = None
        
        pg.mixer.init()
        self.MUSIC_END = pg.USEREVENT + 1
        pg.mixer.music.set_endevent(self.MUSIC_END)
        self.jouer_musique_aleatoire()
        self.ambiance = pg.mixer.Sound("assets/musique/ambiance.wav")
        self.ambiance.set_volume(0.4)
        self.ambiance.play()
        self.ambiance_timer = None
        self.prochaine_musique = 0
        self.attente_musique = False
        
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
            if event.type == self.MUSIC_END:
                if self.etat_jeu != ETAT_PAUSE:
                    self.attente_musique = True
                    self.prochaine_musique = pg.time.get_ticks() + randint(60000, 120000) 

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

            elif self.etat_jeu == ETAT_FIN:
                elapsed = pg.time.get_ticks() - self.fin_start_time
                if elapsed > 17309:
                    self.play = False 

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

                    elif keys[pg.K_a] and keys[pg.K_z] and keys[pg.K_e] and self.etape_histoire >= 3:
                        gatouz = next((p for p in self.npcs if p.name == "Gatouz"), None)
                        if gatouz:
                            self.player.rect.center = (gatouz.rect.centerx - 150, gatouz.rect.centery)
                            self.player.posix, self.player.posiy = self.player.rect.center
                        for pnj in self.npcs:
                            if pnj.name not in ("Gatouz",):
                                pnj.rect.center = (-500, -500)
                                pnj.chemin = []
                        self.etape_histoire = 9
                        self.soir_start_time = pg.time.get_ticks()
                        self.etat_jeu = ETAT_JEU
                        print("Debug : Skip vers event 9 (Plage soir)")
                    elif event.key == pg.K_ESCAPE:
                        self.etat_jeu = ETAT_PAUSE
                        self.ambiance.stop()
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

                                        # Event 1 : Luna part vers la clairière
                                        if event_id == 1: 
                                            luna = next((p for p in self.npcs if p.name == "Luna"), None)
                                            if luna:
                                                chemin_luna = [(3814, 4404), (3814, 3340), (4810, 3340), (4810, 2965), (5500, 2965), (5500, 2750), (5728, 2750)]
                                                luna.donner_chemin(chemin_luna)
                                                
                                        # Event 2 : on passe en scène C
                                        elif event_id == 2:
                                            self.scene_actuelle = "C"
                                            
                                        # Event 3 : fin intro clairière → free roam
                                        elif event_id == 3 and self.etape_histoire == 2:
                                            etat_prochain = ETAT_CINEMATIQUE 
                                            self.scene_actuelle = "TRANS_B_FREE"
                                            self.fondu_sens = 1
                                            self.fondu_start = pg.time.get_ticks()
                                            self.fondu_duree = 1500

                                        # Event 4 : fin dialogue Gatouz plage →
                                        #   Kiko au camp, tous les autres hors-map,
                                        #   le joueur marche seul
                                        elif event_id == 4:
                                            kiko   = next((p for p in self.npcs if p.name == "Kiko"),   None)
                                            luna   = next((p for p in self.npcs if p.name == "Luna"),   None)
                                            wina   = next((p for p in self.npcs if p.name == "Wina"),   None)
                                            spensi = next((p for p in self.npcs if p.name == "Spensi"), None)
                                            gatouz = next((p for p in self.npcs if p.name == "Gatouz"), None)
                                            if kiko:
                                                kiko.rect.center = (5843, 2484)
                                                kiko.posix, kiko.posiy = kiko.rect.center
                                                kiko.chemin = []
                                                kiko.state = "IL"
                                                kiko.current_frame = 0
                                                kiko.image = kiko.animations["IL"][0]
                                            for pnj in [luna, wina, spensi]:
                                                if pnj:
                                                    pnj.rect.center = (-500, -500)
                                                    pnj.chemin = []
                                            self.etape_histoire = 5
                                            self.scene_actuelle = None

                                        # Event 5 : Kiko dit "suis-moi", il marche
                                        elif event_id == 5:
                                            kiko = next((p for p in self.npcs if p.name == "Kiko"), None)
                                            if kiko:
                                                kiko.donner_chemin([
                                                    (5335, 2484), (5323, 2140),
                                                    (4835, 2140), (4711, 2140),
                                                ])
                                            self.etape_histoire = 6

                                        # Event 6 : Kiko panique → Spensi spawn + marche
                                        elif event_id == 6:
                                            spensi = next((p for p in self.npcs if p.name == "Spensi"), None)
                                            if spensi:
                                                spensi.rect.center = (5843, 2484)
                                                spensi.posix, spensi.posiy = spensi.rect.center
                                                spensi.state = "IL"
                                                spensi.current_frame = 0
                                                spensi.image = spensi.animations["IL"][0]
                                                spensi.donner_chemin([
                                                    (5335, 2484), (5323, 2140),
                                                    (5100, 2140),
                                                ])
                                            self.etape_histoire = 7

                                        # Event 7 : Spensi explique → les 2 repartent
                                        #   Spensi devant, Kiko derrière
                                        elif event_id == 7:
                                            kiko   = next((p for p in self.npcs if p.name == "Kiko"),   None)
                                            spensi = next((p for p in self.npcs if p.name == "Spensi"), None)
                                            # Spensi (à 5100) part directement vers la droite
                                            if spensi:
                                                spensi.donner_chemin([
                                                    (5323, 2140), (5323, 2575),
                                                    (6867, 2575), (6867, 1782),
                                                ])
                                            # Kiko (à 4711) suit derrière
                                            if kiko:
                                                kiko.donner_chemin([
                                                    (4835, 2140), (5323, 2140),
                                                    (5323, 2575), (6867, 2575),
                                                    (6867, 1962), (6735, 1962),
                                                ])
                                            self.bois_actif = True
                                            self.etape_histoire = 8
                                            
                                        elif event_id == 9:
                                            wina = next((p for p in self.npcs if p.name == "Wina"), None)
                                            gatouz = next((p for p in self.npcs if p.name == "Gatouz"), None)
                                            if wina and gatouz:
                                                gx, gy = gatouz.rect.centerx, gatouz.rect.centery
                                                wina.rect.center = (gx - 600, gy - 100)
                                                wina.posix, wina.posiy = wina.rect.center
                                                wina.state = "IR"
                                                wina.current_frame = 0
                                                wina.image = wina.animations["IR"][0]
                                                wina.donner_chemin([(gx - 80, gy - 100)])
                                            self.etape_histoire = 10

                                        elif event_id == 10:
                                            etat_prochain = ETAT_CINEMATIQUE
                                            self.scene_actuelle = "TRANS_PLAGE_CAMP"
                                            self.fondu_sens = 1
                                            self.fondu_start = pg.time.get_ticks()
                                            self.fondu_duree = 1500
                                            self.etape_histoire = 11

                                        elif event_id == 11:
                                            etat_prochain = ETAT_CINEMATIQUE
                                            self.scene_actuelle = "TRANS_TO_FIN"
                                            self.fondu_sens = 1
                                            self.fondu_start = pg.time.get_ticks()
                                            self.fondu_duree = 2000

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
                    self.ambiance.play() 

    def mettre_a_jour(self):
        self.verifier_declencheurs_histoire()
        if self.attente_musique:
            if pg.time.get_ticks() >= self.prochaine_musique:
                self.jouer_musique_aleatoire()
                self.attente_musique = False
        if self.ambiance_timer is not None:
            if pg.time.get_ticks() - self.ambiance_timer > 10000: 
                self.ambiance.play()
                self.ambiance_timer = None
        elif self.etat_jeu != ETAT_PAUSE and not self.ambiance.get_num_channels():  
            self.ambiance_timer = pg.time.get_ticks()
            
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
            self.camera_y = self.player.posiy - HAUTEUR // 2 - 32

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
                    self.etape_histoire = 2
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

        # --- TRANS_B_FREE : fin intro clairière → free roam ---
        elif self.scene_actuelle == "TRANS_B_FREE":
            if self.fondu_sens == 1:
                self.fondu_alpha = int(progression * 255)
                if progression >= 1.0:
                    gatouz = next((p for p in self.npcs if p.name == "Gatouz"), None)
                    if gatouz:
                        gatouz.rect.midbottom = (6295, 8964) 
                        gatouz.state = "IR"
                    
                    self.etape_histoire = 3                    
                    self.fondu_sens = -1
                    self.fondu_start = pg.time.get_ticks()

            elif self.fondu_sens == -1:
                self.fondu_alpha = max(0, 255 - int(progression * 255))
                if progression >= 1.0:
                    self.fondu_start = None
                    self.scene_actuelle = "B_FREE"
                    self.etat_jeu = ETAT_JEU

        elif self.scene_actuelle == "TRANS_PLAGE_CAMP":
            if self.fondu_sens == 1:
                self.fondu_alpha = int(progression * 255)
                if progression >= 1.0:
                    self.player.rect.midbottom = (5695, 2920)
                    self.player.posix, self.player.posiy = 5695, 2920
                    for p in self.npcs:
                        if p.name == "Luna":    p.rect.midbottom = (5715, 2808)
                        elif p.name == "Gatouz": p.rect.midbottom = (5799, 2694)
                        elif p.name == "Wina":   p.rect.midbottom = (6035, 2822)
                        elif p.name == "Kiko":   p.rect.midbottom = (6047, 2914)
                        elif p.name == "Spensi": p.rect.midbottom = (5960, 2718)
                        p.posix, p.posiy = p.rect.center

                    data = Dialogue.get_premier("Gatouz", 11)
                    if data:
                        self.charger_dialogue(data)

                    self.fondu_sens = -1
                    self.fondu_start = pg.time.get_ticks()

            elif self.fondu_sens == -1:
                self.fondu_alpha = max(0, 255 - int(progression * 255))
                if progression >= 1.0:
                    self.fondu_start = None
                    self.scene_actuelle = "CAMP_FEU"
                    self.etat_jeu = ETAT_DIALOGUE

        elif self.scene_actuelle == "TRANS_TO_FIN":
            if self.fondu_sens == 1:
                self.fondu_alpha = int(progression * 255)
                if progression >= 1.0:
                    self.etat_jeu = ETAT_FIN
                    self.fin_start_time = pg.time.get_ticks()
                    self.fin_fondu_start = pg.time.get_ticks()

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

        elif self.etat_jeu == ETAT_FIN:
            self.screen.fill((0, 0, 0))
            hauteur_ligne = 40
            start_y = (HAUTEUR - len(self.fin_lines) * hauteur_ligne) // 2
            for i, phrase in enumerate(self.fin_lines):
                text_surf = self.font_intro.render(phrase, True, (255, 255, 255))
                self.screen.blit(text_surf, text_surf.get_rect(center=(LARGEUR // 2, start_y + i * hauteur_ligne)))
            if self.fin_fondu_start is None:
                self.fin_fondu_start = pg.time.get_ticks()
            elapsed_fondu = pg.time.get_ticks() - self.fin_fondu_start
            alpha = max(0, 255 - int((elapsed_fondu / 6580) * 255))
            self.fondu_surface.set_alpha(alpha)
            self.screen.blit(self.fondu_surface, (0, 0))

        elif self.etat_jeu in (ETAT_JEU, ETAT_DIALOGUE, ETAT_CINEMATIQUE, ETAT_PAUSE):
            self.screen.fill(BLANC)
            self.screen.blit(self.map_surface, (-self.camera_x, -self.camera_y))
            
            entites_a_dessiner = self.npcs + [self.player]
            entites_a_dessiner.sort(key=lambda entite: entite.rect.bottom)
            for entite in entites_a_dessiner:
                entite.draw(self.screen, self.camera_x, self.camera_y)

            if self.bois_actif:
                self.screen.blit(
                    self.bois_image,
                    (self.bois_rect.x - self.camera_x,
                     self.bois_rect.y - self.camera_y)
                )

            if self.etat_jeu == ETAT_PAUSE:
                overlay = pg.Surface((LARGEUR, HAUTEUR))
                overlay.set_alpha(140)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                pause_rect = self.txt_pause_grand.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 150))
                self.screen.blit(self.txt_pause_grand, pause_rect)

                controles = [
                    "Z Q S D - Deplacements",
                    "E ou ENTREE - Interagir avec les personnages",
                    "E ou ENTREE - Passer les dialogues",
                    "ECHAP - Mettre le jeu en pause",
                ]

                for i, ligne in enumerate(controles):
                    surf = self.font.render(ligne, True, (255, 255, 255))
                    self.screen.blit(surf, surf.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 20 + i * 45)))

            if self.etat_jeu == ETAT_DIALOGUE:
                self.draw_dialogue()

            if self.etape_histoire >= 9:
                if self.soir_start_time is None:
                    self.soir_start_time = pg.time.get_ticks()
                elapsed = pg.time.get_ticks() - self.soir_start_time
                alpha = min(110, int((elapsed / 99999) * 110))
                self.soir_overlay.set_alpha(alpha)
                self.screen.blit(self.soir_overlay, (0, 0))

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

        # Étape 1 : Luna arrive → cinématique clairière
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

        # Étape 3 : le joueur marche jusqu'à Gatouz et lui parle (via E)
        # Étape 5 : le joueur parle à Kiko (via E)
        # → Pas de trigger auto pour ces deux là.

        # Étape 6 : Kiko arrivé → dialogue panique auto
        elif self.etape_histoire == 6:
            kiko = next((p for p in self.npcs if p.name == "Kiko"), None)
            if kiko and not kiko.chemin:
                if (abs(kiko.rect.centerx - 4711) < 80
                        and abs(kiko.rect.centery - 2140) < 80
                        and abs(self.player.posix - kiko.rect.centerx) < 500
                        and abs(self.player.posiy - kiko.rect.centery) < 400):
                    data = Dialogue.get_premier("Kiko", 6)
                    if data:
                        self.current_speaker_name = "Kiko"
                        self.current_speaker_obj = kiko
                        self.charger_dialogue(data)
                        self.etat_jeu = ETAT_DIALOGUE

        # Étape 7 : Spensi arrivé → dialogue explication auto
        elif self.etape_histoire == 7:
            spensi = next((p for p in self.npcs if p.name == "Spensi"), None)
            if spensi and not spensi.chemin:
                if (abs(spensi.rect.centerx - 5100) < 80
                        and abs(spensi.rect.centery - 2140) < 80):
                    data = Dialogue.get_premier("Spensi", 7)
                    if data:
                        self.current_speaker_name = "Spensi"
                        self.current_speaker_obj = spensi
                        self.charger_dialogue(data)
                        self.etat_jeu = ETAT_DIALOGUE

        # Étape 8 : joueur marche sur le bois → il disparaît
        elif self.etape_histoire == 8:
            if self.bois_actif and self.player.rect.colliderect(self.zone_bois):
                self.bois_actif = False
                self.etape_histoire = 9

        elif self.etape_histoire == 10:
            wina = next((p for p in self.npcs if p.name == "Wina"), None)
            gatouz = next((p for p in self.npcs if p.name == "Gatouz"), None)
            if wina and gatouz and not wina.chemin:
                if abs(wina.rect.centerx - (gatouz.rect.centerx - 80)) < 80:
                    wina.state = "ID"
                    wina.current_frame = 0
                    wina.image = wina.animations["ID"][0]
                    data = Dialogue.get_premier("Wina", 10)
                    if data:
                        self.current_speaker_name = "Wina"
                        self.current_speaker_obj = wina
                        self.charger_dialogue(data)
                        self.etat_jeu = ETAT_DIALOGUE
    def jouer_musique_aleatoire(self):
        musiques = [
            "assets/musique/Amb1.wav",
            "assets/musique/Amb2.wav",
            "assets/musique/Amb3.wav",
            "assets/musique/Amb4.wav",
            "assets/musique/Amb5.wav",
            "assets/musique/Amb6.wav",
            "assets/musique/Amb7.wav",
            "assets/musique/Amb5-1.wav",
            "assets/musique/Guit2.wav",
            "assets/musique/Guit3.wav",
            "assets/musique/Guitt.wav",
            "assets/musique/Guit1-1.wav",
            "assets/musique/Piano3.wav",
            "assets/musique/Siff-1.wav",
            "assets/musique/Siff-2.wav",
        ]
        pg.mixer.music.load(choice(musiques))
        pg.mixer.music.set_volume(choice([0.15, 0.2, 0.25]))
        pg.mixer.music.play()
