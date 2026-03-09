import sqlite3

class Dialogue:
    @staticmethod
    def dialogue(name, ordre):
        connexion = sqlite3.connect('sources/dialogues.db')
        cursor = connexion.cursor()

        query = "SELECT txt, emotion FROM dialogues WHERE npc = ? AND ordre = ?"
        cursor.execute(query, (name, ordre))
        
        resultat = cursor.fetchone()
        connexion.close()

        if resultat:
            return resultat[0], resultat[1]
        return None, None