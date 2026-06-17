from config import VP_ID
from database import get_connection


def est_admin(user_id):
    return user_id == VP_ID


def lire_historique():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nom,message,date FROM historique ORDER BY id DESC")
    donnees = cursor.fetchall()
    conn.close()
    return donnees


async def historique(update, context):
    user_id = update.effective_user.id
    if not est_admin(user_id):
        await update.message.reply_text("Commande réservée au Vice-président.")
        return
    lignes = lire_historique()
    texte = ""
    for nom, message, date in lignes:
        texte += f"{date}\n{nom}\n{message}\n\n"
    await update.message.reply_text(texte[:4000])
