import pygame as pg
from sources.constants import *
from sources.database import Dialogue


class StoryManager:
    def __init__(self, game):
        self.game = game

    # =========================================================================
    # 1. DÉCLENCHEURS CONTINUS (Vérifiés à chaque frame pendant ETAT_JEU)
    # =========================================================================
    def verifier_declencheurs(self):
        etape = self.game.etape_histoire
        player = self.game.player
        npcs = self.game.npcs

        # Étape 1 : Luna est arrivée à la clairière et le joueur la rejoint
        if etape == 1:
            luna = npcs["Luna"]
            if not luna.chemin and luna.rect.x > 5700:
                dist_x = abs(player.posix - luna.rect.centerx)
                dist_y = abs(player.posiy - luna.rect.centery)
                if dist_x < 313 or dist_y < 251:
                    self.lancer_scene_clairiere()

        # Étape 6 : Kiko est arrivé et panique automatiquement quand le joueur approche
        elif etape == 6:
            kiko = npcs["Kiko"]
            if not kiko.chemin:
                if (abs(kiko.rect.centerx - 4711) < 80
                        and abs(kiko.rect.centery - 2140) < 80
                        and abs(player.posix - kiko.rect.centerx) < 500
                        and abs(player.posiy - kiko.rect.centery) < 400):
                    self.game.demarrer_dialogue_pnj("Kiko", 6)

        # Étape 7 : Spensi est arrivé et explique la situation
        elif etape == 7:
            spensi = npcs["Spensi"]
            if not spensi.chemin:
                if (abs(spensi.rect.centerx - 5100) < 80
                        and abs(spensi.rect.centery - 2140) < 80):
                    self.game.demarrer_dialogue_pnj("Spensi", 7)

        # Étape 8 : Le joueur ramasse le bois au sol
        elif etape == 8:
            if self.game.bois_actif and player.rect.colliderect(self.game.zone_bois):
                self.game.bois_actif = False
                self.game.etape_histoire = 9

        # Étape 10 : Wina rejoint Gatouz sur la plage le soir
        elif etape == 10:
            wina = npcs["Wina"]
            gatouz = npcs["Gatouz"]
            if not wina.chemin:
                if abs(wina.rect.centerx - (gatouz.rect.centerx - 80)) < 80:
                    wina.changer_etat("ID")
                    self.game.demarrer_dialogue_pnj("Wina", 10)

    # =========================================================================
    # 2. ÉVÉNEMENTS DE FIN DE DIALOGUE (Déclenchés quand un dialogue se ferme)
    # =========================================================================
    def executer_evenement_dialogue(self, event_id):
        npcs = self.game.npcs

        # Event 1 : Luna part de la plage vers la clairière
        if event_id == 1:
            npcs["Luna"].donner_chemin([
                (3814, 4404), (3814, 3340), (4810, 3340),
                (4810, 2965), (5500, 2965), (5500, 2750), (5728, 2750)
            ])

        # Event 3 : Fin de la discussion à la clairière -> passage en Free Roam
        elif event_id == 3 and self.game.etape_histoire == 2:
            self.game.lancer_transition(
                duree=1500,
                action_milieu=self._setup_free_roam_plage,
                etat_final=ETAT_JEU
            )

        # Event 4 : Fin du dialogue avec Gatouz sur la plage -> Kiko attend au camp
        elif event_id == 4:
            npcs["Kiko"].placer(5843, 2484, ancre="center", etat="IL")
            for nom in ("Luna", "Wina", "Spensi"):
                npcs[nom].placer(-500, -500, ancre="center")
            self.game.etape_histoire = 5

        # Event 5 : Kiko dit "suis-moi" et part vers le nord-ouest
        elif event_id == 5:
            npcs["Kiko"].donner_chemin([
                (5335, 2484), (5323, 2140), (4835, 2140), (4711, 2140)
            ])
            self.game.etape_histoire = 6

        # Event 6 : Kiko panique -> Spensi apparaît au camp et marche vers eux
        elif event_id == 6:
            spensi = npcs["Spensi"]
            spensi.placer(5843, 2484, ancre="center", etat="IL")
            spensi.donner_chemin([
                (5335, 2484), (5323, 2140), (5100, 2140)
            ])
            self.game.etape_histoire = 7

        # Event 7 : Spensi explique -> Spensi et Kiko partent vers la zone du bois
        elif event_id == 7:
            npcs["Spensi"].donner_chemin([
                (5323, 2140), (5323, 2575), (6867, 2575), (6867, 1782)
            ])
            npcs["Kiko"].donner_chemin([
                (4835, 2140), (5323, 2140), (5323, 2575),
                (6867, 2575), (6867, 1962), (6735, 1962)
            ])
            self.game.bois_actif = True
            self.game.etape_histoire = 8

        # Event 9 : Discussion du soir avec Gatouz -> Wina arrive sur la plage
        elif event_id == 9:
            gatouz = npcs["Gatouz"]
            wina = npcs["Wina"]
            gx, gy = gatouz.rect.centerx, gatouz.rect.centery
            wina.placer(gx - 600, gy - 100, ancre="center", etat="IR")
            wina.donner_chemin([(gx - 80, gy - 100)])
            self.game.etape_histoire = 10

        # Event 10 : Wina ramène le groupe au camp pour la nuit
        elif event_id == 10:
            self.game.etape_histoire = 11
            self.game.lancer_transition(
                duree=1500,
                action_milieu=self._setup_camp_soir,
                etat_final=ETAT_DIALOGUE
            )

        # Event 11 : Fin du chapitre 1 -> Écran de fin
        elif event_id == 11:
            self.game.lancer_transition(
                duree=2000,
                action_milieu=self._setup_ecran_fin,
                etat_final=ETAT_FIN,
                fondu_retour=False
            )

    # =========================================================================
    # 3. MISE EN PLACE DES SCÈNES (Exécutées pendant l'écran noir des fondus)
    # =========================================================================
    def lancer_scene_clairiere(self):
        self.game.player.state = "Idle"
        self.game.lancer_transition(
            duree=1500,
            action_milieu=self._setup_clairiere,
            etat_final=ETAT_DIALOGUE
        )

    def _setup_clairiere(self):
        self.game.etape_histoire = 2
        self.game.player.rect.midbottom = (5695, 2920)
        self.game.player.posix, self.game.player.posiy = 5695, 2920

        npcs = self.game.npcs
        npcs["Luna"].placer(5715, 2808, ancre="midbottom")
        npcs["Gatouz"].placer(5799, 2694, ancre="midbottom")
        npcs["Spensi"].placer(5960, 2718, ancre="midbottom")
        npcs["Wina"].placer(6035, 2822, ancre="midbottom", etat="IL")
        npcs["Kiko"].placer(6047, 2914, ancre="midbottom", etat="IL")

        data = Dialogue.get_premier("Gatouz", 2)
        if data:
            self.game.charger_dialogue(data)

    def _setup_free_roam_plage(self):
        self.game.npcs["Gatouz"].placer(6295, 8964, ancre="midbottom", etat="IR")
        self.game.etape_histoire = 3

    def _setup_camp_soir(self):
        self.game.player.rect.midbottom = (5695, 2920)
        self.game.player.posix, self.game.player.posiy = 5695, 2920

        npcs = self.game.npcs
        npcs["Luna"].placer(5715, 2808, ancre="midbottom")
        npcs["Gatouz"].placer(5799, 2694, ancre="midbottom")
        npcs["Wina"].placer(6035, 2822, ancre="midbottom")
        npcs["Kiko"].placer(6047, 2914, ancre="midbottom")
        npcs["Spensi"].placer(5960, 2718, ancre="midbottom")

        data = Dialogue.get_premier("Gatouz", 11)
        if data:
            self.game.charger_dialogue(data)

    def _setup_ecran_fin(self):
        maintenant = pg.time.get_ticks()
        self.game.fin_start_time = maintenant
        self.game.fin_fondu_start = maintenant

    # =========================================================================
    # 4. RACCOURCIS DE DEBUG (A + Z + E)
    # =========================================================================
    def debug_skip(self):
        if self.game.etape_histoire == 1:
            self.lancer_scene_clairiere()
            print("Debug : Skip vers la Clairière (Scène 2)")

        elif self.game.etape_histoire >= 3:
            gatouz = self.game.npcs["Gatouz"]
            self.game.player.rect.center = (gatouz.rect.centerx - 150, gatouz.rect.centery)
            self.game.player.posix, self.game.player.posiy = self.game.player.rect.center

            for nom, pnj in self.game.npcs.items():
                if nom != "Gatouz":
                    pnj.placer(-500, -500, ancre="center")

            self.game.etape_histoire = 9
            self.game.soir_start_time = pg.time.get_ticks()
            self.game.etat_jeu = ETAT_JEU
            print("Debug : Skip vers event 9 (Plage soir)")