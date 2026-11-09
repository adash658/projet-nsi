import pygame as pg
from random import choice, randint
from pytmx.util_pygame import load_pygame
from sources.constants import *
from sources.player import *
from sources.npc import NPC
from sources.Tile import Tile, CollisionTile, PolygonCollisionTile
from sources.database import Dialogue
from sources.story import StoryManager

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

        # Carte et collisions
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

        # Joueur
        self.player = Player(1167, 4404)
        self.player.direction = "right"
        self.player.state = "Idle"
        self.player.image = self.player.animations["Idle"]["right"][0]

        # Dictionnaire des PNJ (accès direct par nom)
        self.npcs = {
            "Luna": NPC("Luna", 1250, 4404, "IL"),
            "Gatouz": NPC("Gatouz", 0, 0),
            "Wina": NPC("Wina", 0, 0),
            "Spensi": NPC("Spensi", 0, 0),
            "Kiko": NPC("Kiko", 0, 0),
        }

        # Gestionnaire d'histoire
        self.story = StoryManager(self)

        self.camera_x = 0
        self.camera_y = 0

        # Polices et Interface
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

        # Intro & Fin
        self.intro_lines = ["12:34 - AN 56 - 07 AOUT", "", """59° 2?' ??" N, 18° 5?' ??" E""", "", "Day One"]
        self.intro_start_time = 0
        self.intro_duration = 5658

        self.fin_lines = ["Day 1", "", "La nuit tombe sur l'île.", "", "End of Chapter 1", "To be continued"]
        self.fin_start_time = 0
        self.fin_fondu_start = None

        # Dialogues
        self.current_dialogue_data = None
        self.current_speaker_name = None
        self.current_speaker_obj = None
        self.current_emotion = None
        self.current_portrait_surface = None
        self.dialogue_pages = []
        self.current_page = 0
        self.en_attente_choix = False

        # Objets interactifs (Bois)
        self.bois_actif = False
        self.bois_image = pg.transform.scale_by(pg.image.load("assets/bois.png").convert_alpha(), 4)
        self.bois_rect = self.bois_image.get_rect(center=(7007, 1786))
        self.zone_bois = self.bois_rect.inflate(32, 32)

        # Système générique de transition / fondu
        self.fondu_alpha = 255
        self.fondu_surface = pg.Surface((LARGEUR, HAUTEUR))
        self.fondu_surface.fill((0, 0, 0))
        self.fondu_sens = -1
        self.fondu_duree = 1500
        self.fondu_start = None
        self.transition_action = None
        self.transition_etat_final = ETAT_JEU
        self.transition_fondu_retour = True

        # Filtre du soir
        self.soir_overlay = pg.Surface((LARGEUR, HAUTEUR))
        self.soir_overlay.fill((10, 10, 40))
        self.soir_start_time = None

        # Audio
        pg.mixer.init()
        self.MUSIC_END = pg.USEREVENT + 1
        pg.mixer.music.set_endevent(self.MUSIC_END)
        self.derniere_musique = "assets/musique/ambiance.wav"
        pg.mixer.music.load(self.derniere_musique)
        pg.mixer.music.set_volume(0.25)
        pg.mixer.music.play()
        self.prochaine_musique = 0
        self.attente_musique = False

    def run(self):
        while self.play:
            self.horloge.tick(FPS)
            self.gerer_evenements()
            self.mettre_a_jour()
            self.dessiner()
        pg.quit()

    # =========================================================================
    # SYSTÈME DE TRANSITION UNIVERSEL
    # =========================================================================
    def lancer_transition(self, duree, action_milieu=None, etat_final=ETAT_JEU, fondu_retour=True):
        """Lance un fondu au noir, exécute `action_milieu` à l'écran noir, puis rallume."""
        self.etat_jeu = ETAT_CINEMATIQUE
        self.fondu_duree = duree
        self.fondu_sens = 1
        self.fondu_start = pg.time.get_ticks()
        self.transition_action = action_milieu
        self.transition_etat_final = etat_final
        self.transition_fondu_retour = fondu_retour

    def mettre_a_jour_transition(self):
        if self.fondu_start is None:
            return

        progression = min(1.0, (pg.time.get_ticks() - self.fondu_start) / self.fondu_duree)

        # Phase 1 : Fondu vers le noir
        if self.fondu_sens == 1:
            self.fondu_alpha = int(progression * 255)
            if progression >= 1.0:
                if self.transition_action:
                    self.transition_action()
                    self.transition_action = None

                if self.transition_fondu_retour:
                    self.fondu_sens = -1
                    self.fondu_start = pg.time.get_ticks()
                else:
                    self.fondu_start = None
                    self.etat_jeu = self.transition_etat_final

        # Phase 2 : Retour vers l'image
        elif self.fondu_sens == -1:
            self.fondu_alpha = max(0, 255 - int(progression * 255))
            if progression >= 1.0:
                self.fondu_start = None
                self.etat_jeu = self.transition_etat_final

    # =========================================================================
    # BOUCLE D'ÉVÉNEMENTS ET MISE À JOUR
    # =========================================================================
    def gerer_evenements(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.play = False

            if event.type == self.MUSIC_END:
                if self.etat_jeu != ETAT_PAUSE:
                    self.attente_musique = True
                    self.prochaine_musique = pg.time.get_ticks() + randint(2202, 170309)

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
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                    mouse_x, mouse_y = pg.mouse.get_pos()
                    print(f"Curseur Map : x={mouse_x + self.camera_x}, y={mouse_y + self.camera_y}")

                if event.type == pg.KEYDOWN:
                    keys = pg.key.get_pressed()
                    if keys[pg.K_a] and keys[pg.K_z] and keys[pg.K_e]:
                        self.story.debug_skip()
                    elif event.key == pg.K_ESCAPE:
                        self.etat_jeu = ETAT_PAUSE
                        pg.mixer.music.pause()
                    elif event.key == pg.K_p:
                        print(f"Position Joueur : x={self.player.rect.centerx}, y={self.player.rect.centery}")
                    elif event.key in (pg.K_e, pg.K_RETURN):
                        self.tenter_interaction_pnj()

            elif self.etat_jeu == ETAT_DIALOGUE:
                if event.type == pg.KEYDOWN:
                    self.gerer_touches_dialogue(event.key)

            elif self.etat_jeu == ETAT_PAUSE:
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.etat_jeu = ETAT_JEU
                    pg.mixer.music.unpause()

    def tenter_interaction_pnj(self):
        npc_name = self.player.check_interaction(self.npcs.values())
        if not npc_name:
            return

        pnj_cible = self.npcs.get(npc_name)
        if not pnj_cible or pnj_cible.chemin:
            return

        dx = self.player.posix - pnj_cible.rect.centerx
        dy = self.player.posiy - pnj_cible.rect.centery

        if abs(dx) > abs(dy):
            etat_voulu = "IR" if dx > 0 else "IL"
        else:
            etat_voulu = "ID" if dy > 0 else "IU"

        interaction_autorisee = False
        if len(pnj_cible.animations.get(etat_voulu, [])) > 0:
            pnj_cible.changer_etat(etat_voulu)
            interaction_autorisee = True
        elif pnj_cible.state[-1] == etat_voulu[-1]:
            interaction_autorisee = True

        if interaction_autorisee:
            self.demarrer_dialogue_pnj(npc_name, self.etape_histoire)

    def demarrer_dialogue_pnj(self, npc_name, etape):
        data = Dialogue.get_premier(npc_name, etape)
        if data:
            self.current_speaker_name = npc_name
            self.current_speaker_obj = self.npcs.get(npc_name)
            self.charger_dialogue(data)
            self.etat_jeu = ETAT_DIALOGUE

    def gerer_touches_dialogue(self, key):
        if key in (pg.K_e, pg.K_RETURN) and not self.en_attente_choix:
            if self.current_page < len(self.dialogue_pages) - 1:
                self.current_page += 1
            else:
                _id, speaker, event_str, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z = self.current_dialogue_data
                if choix_a and choix_z:
                    self.en_attente_choix = True
                elif next_id:
                    self.charger_dialogue(Dialogue.get_par_id(next_id))
                else:
                    self.fermer_dialogue()
                    self.etat_jeu = ETAT_JEU
                    if event_str is not None:
                        self.story.executer_evenement_dialogue(int(event_str))

        elif key == pg.K_a and self.en_attente_choix:
            next_id_a = self.current_dialogue_data[7]
            if next_id_a:
                self.charger_dialogue(Dialogue.get_par_id(next_id_a))
            else:
                self.fermer_dialogue()
                self.etat_jeu = ETAT_JEU

        elif key == pg.K_z and self.en_attente_choix:
            next_id_z = self.current_dialogue_data[9]
            if next_id_z:
                self.charger_dialogue(Dialogue.get_par_id(next_id_z))
            else:
                self.fermer_dialogue()
                self.etat_jeu = ETAT_JEU

    def mettre_a_jour(self):
        if self.etat_jeu == ETAT_JEU:
            self.story.verifier_declencheurs()

        if self.attente_musique and pg.time.get_ticks() >= self.prochaine_musique:
            self.jouer_musique_aleatoire()
            self.attente_musique = False

        if self.etat_jeu == ETAT_INTRO:
            if pg.time.get_ticks() - self.intro_start_time > self.intro_duration:
                self.etat_jeu = ETAT_JEU
                self.fondu_start = pg.time.get_ticks()

        elif self.etat_jeu in (ETAT_JEU, ETAT_CINEMATIQUE):
            for pnj in self.npcs.values():
                if pnj.chemin:
                    pnj.suivre_chemin()
                pnj.animate()

            if self.etat_jeu == ETAT_JEU:
                obstacles = list(self.collisions) + [pnj.rect for pnj in self.npcs.values()]
                self.player.move(obstacles)

            self.camera_x = self.player.posix - LARGEUR // 2
            self.camera_y = self.player.posiy - HAUTEUR // 2 - 32

        if self.etat_jeu == ETAT_CINEMATIQUE:
            self.mettre_a_jour_transition()

    # =========================================================================
    # RENDU & AFFICHAGE
    # =========================================================================
    def dessiner(self):
        if self.etat_jeu == ETAT_MENU:
            self.screen.blit(self.ecran_titre, (0, 0))
            bouton = self.play_pressed_button if self.button_pressed else self.play_button
            self.screen.blit(bouton, self.play_rect)

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

            entites_a_dessiner = list(self.npcs.values()) + [self.player]
            entites_a_dessiner.sort(key=lambda entite: entite.rect.bottom)
            for entite in entites_a_dessiner:
                entite.draw(self.screen, self.camera_x, self.camera_y)

            if self.bois_actif:
                self.screen.blit(
                    self.bois_image,
                    (self.bois_rect.x - self.camera_x, self.bois_rect.y - self.camera_y)
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
                    if self.fondu_alpha == 0:
                        self.fondu_start = None
                self.fondu_surface.set_alpha(self.fondu_alpha)
                self.screen.blit(self.fondu_surface, (0, 0))

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
                        (x * self.tmx_data.tilewidth * 4, y * self.tmx_data.tileheight * 4)
                    )

    # =========================================================================
    # GESTION DES DIALOGUES
    # =========================================================================
    def draw_dialogue(self):
        if not self.current_dialogue_data:
            return

        _id, speaker, event, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z = self.current_dialogue_data

        box_rect = pg.Rect(200, HAUTEUR - 250, LARGEUR - 400, 200)
        pg.draw.rect(self.screen, (0, 0, 0), box_rect)
        pg.draw.rect(self.screen, (255, 255, 255), box_rect, 5)

        if self.current_portrait_surface:
            self.screen.blit(self.current_portrait_surface, (box_rect.x, box_rect.y - 256))

        couleur_nom = COULEURS_PNJ.get(self.current_speaker_name, (255, 255, 0))
        nom_surface = self.font.render(self.current_speaker_name, True, couleur_nom)
        self.screen.blit(nom_surface, (box_rect.x + 20, box_rect.y + 10))

        text_wrap_rect = pg.Rect(box_rect.x + 20, box_rect.y + 50, box_rect.width - 40, box_rect.height - 70)

        if self.en_attente_choix:
            surf_a = self.font.render(f"[A]  {choix_a}", True, (173, 200, 222))
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

        return [lignes[i:i + max_lignes] for i in range(0, len(lignes), max_lignes)]

    def charger_dialogue(self, data):
        if data is None:
            self.fermer_dialogue()
            return

        _id, speaker, event, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z = data

        self.current_dialogue_data = data
        self.current_speaker_name = speaker
        self.current_emotion = emotion
        self.current_speaker_obj = self.npcs.get(speaker)

        # Pré-calcul du portrait une seule fois au chargement de la réplique
        if self.current_emotion and self.current_speaker_obj and self.current_emotion in self.current_speaker_obj.portraits:
            image_brute = self.current_speaker_obj.portraits[self.current_emotion]
            self.current_portrait_surface = preparer_portrait(image_brute, 256, 10)
        else:
            self.current_portrait_surface = None

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
        self.current_portrait_surface = None
        self.dialogue_pages = []
        self.current_page = 0
        self.en_attente_choix = False
        self.player.unlock()

    def jouer_musique_aleatoire(self):
        musiques = [
            "assets/musique/ambiance.wav",
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
        
        # On exclut la musique qui vient de passer
        choix_possibles = [m for m in musiques if m != self.derniere_musique]
        morceau_choisi = choice(choix_possibles)
        self.derniere_musique = morceau_choisi

        pg.mixer.music.load(morceau_choisi)
        pg.mixer.music.set_volume(choice([0.15, 0.2, 0.25]))
        pg.mixer.music.play()