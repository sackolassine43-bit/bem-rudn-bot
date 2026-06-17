from database import get_connection


def changer_disponibilite(nom, etat):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE membres SET disponibilite=? WHERE nom=?", (etat, nom))
    conn.commit()
    conn.close()


ETATS_DISPO = ["disponible", "occupé", "absent"]
