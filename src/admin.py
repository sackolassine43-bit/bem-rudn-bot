from datetime import datetime
import shutil

from database import fetchall
from historique import total_messages


ADMIN_USERNAME = "Lassine223"


def est_admin(username):
    if not username:
        return False

    return username.lower() == ADMIN_USERNAME.lower()


def statistiques():
    utilisateurs = fetchall(
        "SELECT COUNT(*) FROM utilisateurs"
    )[0][0]

    tickets = fetchall(
        "SELECT COUNT(*) FROM tickets"
    )[0][0]

    signalements = fetchall(
        "SELECT COUNT(*) FROM signalements"
    )[0][0]

    messages = total_messages()

    return (
        f"👥 Utilisateurs : {utilisateurs}\n"
        f"💬 Messages : {messages}\n"
        f"🎫 Tickets : {tickets}\n"
        f"⚠️ Signalements : {signalements}"
    )


def historique_admin(limit=50):
    lignes = fetchall(
        """
        SELECT
            nom,
            message,
            date_message
        FROM historique
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    resultat = []

    for nom, message, date in lignes:
        resultat.append(
            f"[{date}] {nom} : {message}"
        )

    return "\n".join(resultat)


def sauvegarder_base():
    nom_fichier = (
        "backups/bem_rudn_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".db"
    )

    shutil.copy(
        "data/bem_rudn.db",
        nom_fichier
    )

    return nom_fichier


def panneau_admin():
    return """
🔐 PANNEAU ADMIN

/stats
/historique
/backup
/broadcast

Accès réservé.
"""
def stats_text():
    return statistiques()

def backup_database():
    return sauvegarder_base()

async def broadcast_message(bot, message):
    utilisateurs = fetchall("SELECT telegram_id FROM utilisateurs")
    for u in utilisateurs:
        try:
            await bot.send_message(chat_id=u[0], text=message)
        except:
            pass

def panel_admin():
    return panneau_admin()

def historique_recent(limit=50):
    return historique_admin(limit)

def chercher_reponse(question, connaissances, seuil=60):
    from fuzzy import meilleur_match
    mot, score = meilleur_match(question, list(connaissances.keys()))
    if score >= seuil:
        return connaissances[mot]
    return "Aucune réponse trouvée."
