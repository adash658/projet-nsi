readme.md

GLADE - PROTOCOLE D UTILISATION

PROJET TROPHEES NSI 2026
Equipe : Adrien Darras, Artheesan, Berenice et Augustin (Lycee Louis le Grand, classe de 1ere).

DESCRIPTION DU JEU
Glade est un RPG narratif de survie axe sur l'exploration et les dialogues (cree avec Pygame, PyTMX et SQLite). Note : Ce prototype jouable contient l'integralite du Chapitre 1 (Jour 1 : Le deni et l'organisation).

PREREQUIS
Python 3.10 ou superieur.
Les bibliotheques listees dans le fichier requirements.txt.

Pour installer les dependances, ouvrez un terminal a la racine du projet et tapez :
pip install -r requirements.txt

LANCEMENT
Depuis la racine du projet, tapez la commande suivante :
python main.py

STRUCTURE DU PROJET
main.py : Point d'entree pour lancer le jeu.
requirements.txt : Liste des dependances (pygame, pytmx).
assets/ : Dossier contenant les images, polices et la carte Tiled.
sources/ : Dossier contenant le code source (moteur du jeu, gestion du joueur, des PNJ, et la base de donnees dialogues.db).

CONTROLES
Touches Z Q S D : Se deplacer sur la carte.
Touche E ou Entree : Interagir avec un personnage / Passer a la suite du dialogue.
Touches A ou Z : Faire un choix lors d'un embranchement de dialogue.
Touche Echap : Mettre le jeu en pause / Reprendre la partie.

DEROULEMENT
Le jeu demarre sur un ecran titre. Cliquez sur Play ou appuyez sur Entree pour lancer la sequence d'introduction. Vous prendrez ensuite le controle de votre personnage apres un crash. La progression est lineaire et est validee en allant parler aux differents naufrages (Gatouz, Luna, Wina, Spensi, Kiko) et en explorant l'ile pour faire avancer l'histoire.