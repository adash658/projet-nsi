import sqlite3

class Dialogue:
    @staticmethod
    def get_premier(name, event):
        connexion = sqlite3.connect('sources/dialogues.db')
        cursor = connexion.cursor()
        cursor.execute(
            "SELECT id, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z "
            "FROM dialogues WHERE npc = ? AND event = ? ORDER BY id ASC LIMIT 1",
            (name, event)
        )
        resultat = cursor.fetchone()
        connexion.close()
        return resultat

    @staticmethod
    def get_par_id(dialogue_id):
        connexion = sqlite3.connect('sources/dialogues.db')
        cursor = connexion.cursor()
        cursor.execute(
            "SELECT id, txt, emotion, next_id, choix_a, next_id_a, choix_z, next_id_z "
            "FROM dialogues WHERE id = ?",
            (dialogue_id,)
        )
        resultat = cursor.fetchone()
        connexion.close()
        return resultat