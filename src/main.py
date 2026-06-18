from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN

from database import (
    init_database,
    execute,
)

from membres import (
    get_membres,
    initialiser_membres,
)

from historique import (
    enregistrer_message,
)

from documents import (
    get_documents,
)

from dispo import (
    format_disponibilites,
)

from urgence import (
    est_urgence,
    enregistrer_urgence,
    message_urgence,
)

from connaissances import (
    CONNAISSANCES,
)

from admin import (
    stats as stats_text,
    backup as backup_database,
    broadcast_message,
    panel_admin,
)

from historique import (
    historique_recent,
)

from fuzzy import chercher_reponse

ADMIN_USERNAME = "Lassine223"


def est_admin(update):
    utilisateur = update.effective_user
    return utilisateur.username == ADMIN_USERNAME


# -------------------------
# COMMANDES
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utilisateur = update.effective_user

    execute(
        """
        INSERT OR IGNORE INTO utilisateurs
        (telegram_id, nom, username, date_inscription)
        VALUES (?, ?, ?, datetime('now'))
        """,
        (utilisateur.id, utilisateur.full_name, utilisateur.username),
    )

    texte = (
        "🇲🇱 BEM-RUDN\n\n"
        "Bienvenue.\n\n"
        "Vous pouvez écrire naturellement :\n"
        "• Je veux renouveler mon visa\n"
        "• Je cherche un dortoir\n"
        "• J'ai perdu mon passeport\n"
        "• Documents master\n"
        "• Je viens d'arriver à Moscou"
    )

    await update.message.reply_text(texte)


async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
COMMANDES

/start
/aide
/membres
/documents
/dispo

Vous pouvez aussi écrire vos questions directement.
"""
    )


async def membres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lignes = []

    for membre in get_membres():
        nom, poste, telephone, dispo = membre

        lignes.append(
            f"{poste}\n{nom}\n{telephone}\n{dispo}"
        )

    await update.message.reply_text("\n\n".join(lignes))


async def documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_documents("all"))


async def dispo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_disponibilites())


async def historique(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    await update.message.reply_text(historique_recent(50))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    await update.message.reply_text(stats_text())


async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    fichier = backup_database()
    await update.message.reply_document(open(fichier, "rb"))


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    await update.message.reply_text(panel_admin())


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = sorted(CONNAISSANCES.keys())
    await update.message.reply_text("\n".join(categories))


async def recherche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Usage : /recherche mot")
        return
    mot = " ".join(context.args)
    resultat = chercher_reponse(mot, CONNAISSANCES, seuil=60)
    await update.message.reply_text(resultat)


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    if len(context.args) == 0:
        await update.message.reply_text("Usage : /broadcast message")
        return
    message = " ".join(context.args)
    await broadcast_message(context.bot, message)
    await update.message.reply_text("Message envoyé.")


# -------------------------
# MESSAGES TEXTE
# -------------------------

async def texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utilisateur = update.effective_user
    message = update.message.text

    enregistrer_message(utilisateur.id, utilisateur.full_name, message)

    if est_urgence(message):
        enregistrer_urgence(utilisateur.id, message)
        await update.message.reply_text(message_urgence())
        return

    message_min = message.lower()

    for mot_cle, reponse in CONNAISSANCES.items():
        if mot_cle in message_min:
            await update.message.reply_text(reponse)
            return

    await update.message.reply_text(
        "Je n'ai pas encore trouvé la réponse. Essayez de reformuler votre question."
    )


# -------------------------
# MAIN
# -------------------------

def main():
    init_database()
    initialiser_membres()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aide", aide))
    app.add_handler(CommandHandler("membres", membres))
    app.add_handler(CommandHandler("documents", documents))
    app.add_handler(CommandHandler("dispo", dispo))
    app.add_handler(CommandHandler("historique", historique))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("faq", faq))
    app.add_handler(CommandHandler("recherche", recherche))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texte))

    print("BEM-RUDN BOT démarré...")

    app.run_polling()


if __name__ == "__main__":
    main()
