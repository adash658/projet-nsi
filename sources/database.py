import sqlite3

class Dialogue:
    @staticmethod
    def dialogue(npc, ordre):
        connexion = sqlite3.connect('sources/dialogues.db')
        cursor = connexion.cursor()

        query = "SELECT txt FROM dialogues WHERE npc = ? AND ordre = ?"
        cursor.execute(query, (npc, ordre))
        
        resultat = cursor.fetchone()
        connexion.close()

        return resultat[0] if resultat else None