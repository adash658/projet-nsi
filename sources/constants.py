import pygame as pg

# Fenêtre
LARGEUR = 1200
HAUTEUR = 800
FPS = 60

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)

CHEMIN_POLICE = "assets/fonts/yoster.ttf"
POLICE_INTRO = "assets/fonts/intro.ttf"

COULEURS_PNJ = {
    "Luna": (234, 120, 200), 
    "Gatouz": (151, 64, 32),    
    "Wina": (188, 64, 200),    
    "Spensi": (213, 199, 173),
    "Kiko": (99, 250, 99), 
    "Le Joueur": (200, 220, 222)
}

# Etats
ETAT_MENU = 0
ETAT_INTRO = 1
ETAT_JEU = 2
ETAT_DIALOGUE = 3
ETAT_CINEMATIQUE = 4
ETAT_PAUSE = 5
ETAT_FIN = 6