TITRE DU PROJET
Glade

NOMS DES MEMBRES DU GROUPE
Adrien Darras, Artheesan, Berenice, Augustin (Classe de 1ere, Lycee Louis le Grand).

DESCRIPTION COURTE DU JEU
Glade est un RPG narratif de survie en 2D, axe sur un huis clos psychologique. Six rescapes d'un crash se retrouvent bloques sur une ile de l'archipel de Stockholm. Le jeu repose sur la "Paranoia du Vide" : il n'y a ni monstres ni menace physique externe. Le veritable danger vient de l'epuisement, des mensonges et de la tension qui monte entre les personnages au fil des jours. Le joueur (amnesique) doit interagir avec eux via un systeme de dialogues dynamique pour reparer un bateau et s'echapper.

INSPIRATIONS ET INFLUENCES
Visuellement et dans sa mecanique d'exploration, Glade puise ses inspirations dans plusieurs œuvres marquantes. L'ambiance narrative et le concept de RPG alternatif s'inspirent de jeux independants modernes comme Undertale. Pour l'esthetique globale et la vue de dessus (top-down), le jeu s'inspire grandement des classiques de l'ere Game Boy, tels que les premiers jeux Pokemon ou encore The Legend of Zelda: Link's Awakening DX.

REPARTITION DES TACHES
Adrien : Programmation principale du moteur de jeu et de l'interface, interfacage de Python avec la base de donnees, creation de l'histoire globale et conceptualisation des personnages.
Artheesan : Co-creation de l'univers et des personnages avec Adrien, conception des assets graphiques des PNJ, co-ecriture des dialogues et realisation du menu de pause.
Berenice : Composition, recherche et implementation de la musique, co-ecriture d'une grande partie des dialogues et realisation de l'ecran d'introduction.
Augustin : Integration de la carte (map), developpement de la logique de deplacement du joueur et programmation mathematique du systeme de collisions.

DIFFICULTES RENCONTREES

La gestion globale du temps, qui est devenue tres critique sur la fin du projet et a oblige a cloturer le prototype a la fin du premier jour in-game.

La structuration et la lisibilite du code pour la gestion des evenements narratifs, devenue complexe a maintenir pour Adrien.

La programmation du systeme de collisions avec les differents decors pour Augustin.

La maitrise de Git et Github Desktop pour reussir a travailler a quatre en meme temps tout en gardant un historique propre et en evitant les conflits de code.

RESSOURCES ET OUTILS UTILISES

Langage : Python (version 3.10+)

Bibliotheques tierces : Pygame (moteur graphique, evenements, audio), PyTMX (lecture du format de la carte)

Base de donnees : SQLite3 (pour stocker, structurer et appeler les arbres de dialogues selon les situations)

Outils de developpement : Github Desktop (versioning collaboratif), Tiled (creation de la carte a partir de tuiles).