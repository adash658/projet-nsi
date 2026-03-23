import sqlite3
import csv
import os

def importer_donnees():
    # On récupère les chemins absolus pour être sûr de ne pas se tromper
    chemin_script = os.path.abspath(__file__) # Chemin de setup_db.py
    dossier_sources = os.path.dirname(chemin_script) # Dossier /sources
    dossier_racine = os.path.dirname(dossier_sources) # Dossier racine du projet

    chemin_db = os.path.join(dossier_sources, 'dialogues.db')
    # On cherche le CSV à la RACINE du projet (là où se trouve sans doute ton main.py)
    chemin_csv = os.path.join(dossier_racine, 'dialogues.csv')

    print(f"--- CONFIGURATION DES CHEMINS ---")
    print(f"Base de donnee cible : {chemin_db}")
    print(f"CSV source recherche : {chemin_csv}")
    print(f"---------------------------------")

    # Vérification si le CSV existe avant de faire quoi que ce soit
    if not os.path.exists(chemin_csv):
        print(f"ERREUR : Le fichier 'dialogues.csv' est introuvable !")
        print(f"Assure-toi de l'avoir place dans : {dossier_racine}")
        return

    try:
        conn = sqlite3.connect(chemin_db)
        cursor = conn.cursor()

        # On vide la table actuelle
        cursor.execute("DELETE FROM dialogues")

        with open(chemin_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # On récupère les données. row.get(k) évite de planter si une colonne manque
                vals = [row.get(k) if row.get(k) != "" else None for k in [
                    'id', 'npc', 'event', 'txt', 'emotion', 
                    'next_id', 'choix_a', 'next_id_a', 'choix_z', 'next_id_z'
                ]]
                
                cursor.execute("INSERT INTO dialogues VALUES (?,?,?,?,?,?,?,?,?,?)", vals)
                count += 1

        conn.commit()
        conn.close()
        print(f"SUCCES : {count} lignes importees dans la base de donnees.")
        
    except Exception as e:
        print(f"ERREUR lors de l'import : {e}")

if __name__ == "__main__":
    importer_donnees()