from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TOKEN
from database import init_db
from admin import historique
from urgence import reponse_urgence, MOTS_URGENCE
from fuzzy import trouver_question
from connaissances import CONNAISSANCES
from membres import MEMBRES
from historique import enregistrer_message


async def start(update, context):
    await update.message.reply_text(
        "🇲🇱 BEM-RUDN 2026-2027\n\nBienvenue.\n\nCommandes :\n/bureau\n/dispo\n/parcours\n/urgence\n/historique"
    )


async def gerer_message(update, context):
    user_id = update.effective_user.id
    nom = update.effective_user.full_name or "Inconnu"
    message = update.message.text
    enregistrer_message(user_id, nom, message)
    msg = message.lower()
    
    for mot in MOTS_URGENCE:
        if mot in msg:
            await reponse_urgence(update)
            return
    
    reponse = trouver_question(msg, CONNAISSANCES)
    if reponse:
        await update.message.reply_text(reponse)
        return
    
    for m in MEMBRES:
        if m["nom"].lower() in msg:
            await update.message.reply_text(f"👤 {m['nom']} — {m['poste']}\n📞 {m['telephone']}")
            return
    
    await update.message.reply_text("Commande non reconnue. Tape /start.")


def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("historique", historique))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gerer_message))
    print("Bot lancé...")
    app.run_polling()


if __name__ == "__main__":
    main()
