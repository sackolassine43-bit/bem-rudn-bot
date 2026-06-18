from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config import BOT_TOKEN, MEMBRES_BUREAU
from database import init_database, execute, fetchall, fetchone
from membres import initialiser_membres, get_membres
from historique import enregistrer_message
from documents import get_documents
from dispo import format_disponibilites
from urgence import est_urgence, enregistrer_urgence, message_urgence
from connaissances import CONNAISSANCES
from datetime import datetime

ADMIN_USERNAME = "Lassine223"


def est_admin(update):
    utilisateur = update.effective_user
    return utilisateur.username and utilisateur.username.lower() == ADMIN_USERNAME.lower()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utilisateur = update.effective_user
    execute(
        "INSERT OR IGNORE INTO utilisateurs (telegram_id, nom, username, date_inscription) VALUES (?, ?, ?, datetime('now'))",
        (utilisateur.id, utilisateur.full_name, utilisateur.username),
    )
    await update.message.reply_text(
        "🇲🇱 BEM-RUDN\n\nBienvenue.\n\n"
        "Écrivez votre question simplement.\n"
        "Exemples : visa, dortoir, admission, SIM, banque..."
    )


async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start /aide /membres /documents /dispo /faq /recherche /historique /panel")


async def membres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lignes = []
    for membre in get_membres():
        nom, poste, telephone, dispo = membre
        lignes.append(f"{poste}\n{nom}\n{telephone}\n{dispo}")
    await update.message.reply_text("\n\n".join(lignes))


async def documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_documents("all"))


async def dispo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_disponibilites())


async def historique(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    from admin import historique_admin
    await update.message.reply_text(historique_admin(50))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    from admin import statistiques
    await update.message.reply_text(statistiques())


async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    from admin import sauvegarder_base
    fichier = sauvegarder_base()
    await update.message.reply_document(open(fichier, "rb"))


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    from admin import panneau_admin
    await update.message.reply_text(panneau_admin())


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = sorted(CONNAISSANCES.keys())
    await update.message.reply_text("\n".join(categories))


async def recherche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Usage : /recherche mot")
        return
    mot = " ".join(context.args)
    for cle, reponse in CONNAISSANCES.items():
        if mot in cle:
            await update.message.reply_text(reponse)
            return
    await update.message.reply_text("Aucune réponse trouvée.")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    if len(context.args) == 0:
        await update.message.reply_text("Usage : /broadcast message")
        return
    message = " ".join(context.args)
    utilisateurs = fetchall("SELECT telegram_id FROM utilisateurs")
    for u in utilisateurs:
        try:
            await context.bot.send_message(chat_id=u[0], text=message)
        except:
            pass
    await update.message.reply_text("Message envoyé.")


# ==================== DISPONIBILITÉS MEMBRES ====================
async def gerer_dispo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utilisateur = update.effective_user
    message = update.message.text.lower().strip()
    
    membre = None
    for tel, infos in MEMBRES_BUREAU.items():
        if utilisateur.username and utilisateur.username.lower() == infos.get("telegram", "").lower().replace("@", ""):
            membre = infos
            break
    
    if not membre:
        return None
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if message == "absent":
        execute("UPDATE membres SET disponibilite='absent', horaires='' WHERE nom=?", (membre["nom"],))
        await update.message.reply_text(f"✅ {membre['nom']} — Absent aujourd'hui")
        return True
    
    if message in ["occupé", "occupe"]:
        execute("UPDATE membres SET disponibilite='occupe' WHERE nom=?", (membre["nom"],))
        await update.message.reply_text(f"✅ {membre['nom']} — Occupé (🟡)")
        return True
    
    if message == "dispo journée":
        execute("UPDATE membres SET disponibilite='disponible', horaires='9h-18h' WHERE nom=?", (membre["nom"],))
        await update.message.reply_text(f"✅ {membre['nom']} — Disponible toute la journée (9h-18h)")
        return True
    
    if message.startswith("dispo "):
        horaires = message.replace("dispo ", "").strip()
        execute("UPDATE membres SET disponibilite='disponible', horaires=? WHERE nom=?", (horaires, membre["nom"]))
        await update.message.reply_text(f"✅ {membre['nom']} — Disponible : {horaires}")
        return True
    
    if message == "dispo":
        result = fetchone("SELECT disponibilite, horaires FROM membres WHERE nom=?", (membre["nom"],))
        if result:
            etat, horaires = result
            await update.message.reply_text(
                f"👤 {membre['nom']} — {membre['poste']}\nStatut : {etat}\nHoraires : {horaires or 'Non défini'}"
            )
        return True
    
    return None


# ==================== RECHERCHE CONTACT PAR NOM ====================
def chercher_contact(message):
    message = message.lower()
    for tel, infos in MEMBRES_BUREAU.items():
        if infos["nom"].lower() in message:
            return f"👤 {infos['nom']} — {infos['poste']} {infos['pole']}\n📞 {tel}"
    return None


# ==================== MESSAGES TEXTE ====================
async def texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utilisateur = update.effective_user
    message = update.message.text
    
    enregistrer_message(utilisateur.id, utilisateur.full_name, message)
    
    # 1. Vérifier disponibilité membre
    dispo_result = await gerer_dispo(update, context)
    if dispo_result:
        return
    
    # 2. Vérifier urgence
    if est_urgence(message):
        enregistrer_urgence(utilisateur.id, message)
        await update.message.reply_text(message_urgence())
        return
    
    # 3. Chercher contact par nom
    contact = chercher_contact(message)
    if contact:
        await update.message.reply_text(contact)
        return
    
    # 4. Chercher dans connaissances
    message_min = message.lower()
    for mot_cle, reponse in CONNAISSANCES.items():
        if mot_cle in message_min:
            await update.message.reply_text(reponse)
            return
    
    # 5. Question non trouvée → assistance humaine
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute(
        "INSERT INTO tickets (user_id, probleme, statut, date_creation) VALUES (?, ?, 'ouvert', ?)",
        (utilisateur.id, message, now)
    )
    
    await update.message.reply_text(
        "❌ Je n'ai pas trouvé de réponse précise.\n\n"
        "📨 Votre question a été transmise au responsable compétent du BEM-RUDN.\n\n"
        "⏳ Veuillez patienter pendant qu'un membre du bureau vous répond.\n\n"
        "📞 En cas d'urgence :\n"
        "Président : +79912697921\n"
        "Vice-président : +79912435421\n"
        "Telegram : @Lassine223"
    )


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
