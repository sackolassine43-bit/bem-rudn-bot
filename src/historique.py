from database import get_connection


def enregistrer_message(user_id, nom, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historique(user_id, nom, message) VALUES(?,?,?)",
        (user_id, nom, message)
    )
    conn.commit()
    conn.close()
