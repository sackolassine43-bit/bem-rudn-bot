from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from rapidfuzz import fuzz

from config import BOT_TOKEN, MEMBRES_BUREAU, FUZZY_THRESHOLD
from database import init_database, execute, fetchall, fetchone
from membres import initialiser_membres, get_membres
from historique import enregistrer_message
from documents import get_documents
from dispo import format_disponibilites
from urgence import est_urgence, enregistrer_urgence, message_urgence
from connaissances import CONNAISSANCES
from parcours import ETAPES, get_etape
from datetime import datetime

ADMIN_USERNAME = "Lassine223"


def est_admin(update):
    utilisateur = update.effective_user
    return utilisateur.username and utilisateur.username.lower() == ADMIN_USERNAME.lower()


def fuzzy_search(query, connaissances, threshold=60):
    """Recherche floue dans les connaissances"""
    meilleur_score = 0
    meilleure_cle = None
    query = query.lower().strip()
    for cle in connaissances.keys():
        score = fuzz.ratio(query, cle.lower())
        if score > meilleur_score:
            meilleur_score = score
            meilleure_cle = cle
    if meilleur_score >= threshold:
        return meilleure_cle
    return None


# ==================== COMMANDES ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utilisateur = update.effective_user
    execute(
        "INSERT OR IGNORE INTO utilisateurs (telegram_id, nom, username, date_inscription) VALUES (?, ?, ?, datetime('now'))",
        (utilisateur.id, utilisateur.full_name, utilisateur.username),
    )
    await update.message.reply_text(
        "🇲🇱 BEM-RUDN 2026-2027\n\nBienvenue.\n\n"
        "Écrivez votre question simplement.\n"
        "Exemples : visa, dortoir, admission, SIM, banque...\n\n"
        "Commandes : /start /aide /parcours /dispo /urgence /arrivee /nouveau"
    )


async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 COMMANDES ÉTUDIANTS\n"
        "/start - Accueil\n"
        "/aide - Cette liste\n"
        "/parcours - Voir les 7 étapes\n"
        "/dispo - Disponibilités bureau\n"
        "/arrivee - Guide nouvel arrivant\n"
        "/nouveau - Guide premier jour\n"
        "/urgence - Contacts urgence\n"
        "/membres - Liste du bureau\n"
        "/documents - Documents par niveau"
    )


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


async def parcours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = "📋 LES 7 ÉTAPES DU PARCOURS\n\n"
    for num, etape in ETAPES.items():
        texte += f"{num}. {etape}\n"
    texte += "\n📌 Tapez : étape 1 fait\n📌 Bloqué : bloqué étape 3"
    await update.message.reply_text(texte)


async def etape_fait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère 'étape X fait' ou 'bloqué étape X'"""
    message = update.message.text.lower().strip()
    utilisateur = update.effective_user
    
    if message.startswith("étape ") and "fait" in message:
        try:
            num = int(message.replace("étape ", "").replace(" fait", "").strip())
            if 1 <= num <= 7:
                execute(
                    "INSERT OR IGNORE INTO etudiants (telegram_id, nom, etape) VALUES (?, ?, ?)",
                    (utilisateur.id, utilisateur.full_name, num)
                )
                execute(
                    "UPDATE etudiants SET etape=?, date_modification=datetime('now') WHERE telegram_id=?",
                    (num, utilisateur.id)
                )
                await update.message.reply_text(f"✅ Étape {num} validée : {get_etape(num)}")
                return True
        except:
            pass
    
    if message.startswith("bloqué étape "):
        try:
            num = int(message.replace("bloqué étape ", "").strip())
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            execute(
                "INSERT INTO tickets (user_id, probleme, statut, date_creation) VALUES (?, ?, 'bloqué', ?)",
                (utilisateur.id, f"Étudiant bloqué à l'étape {num}", now)
            )
            await update.message.reply_text(
                f"🔴 ALERTE ENVOYÉE — Bloqué à l'étape {num}.\n"
                "Un responsable BEM-RUDN va vous contacter.\n\n"
                "📞 Urgence : +79912435421"
            )
            return True
        except:
            pass
    
    return None


async def arriver_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛬 GUIDE NOUVEL ARRIVANT\n\n"
        "1️⃣ Aéroport → Campus RUDN\n"
        "   Aeroexpress + métro ou Yandex Go\n\n"
        "2️⃣ Dortoir provisoire\n"
        "   15 rue Miklukho-Maklaya, Bât.1, Salle 2\n\n"
        "3️⃣ MFC RUDN (RdC, 9h-18h)\n"
        "   Enregistrement migration\n\n"
        "4️⃣ Centre médical\n"
        "   10 rue Miklukho-Maklaya\n\n"
        "5️⃣ Carte SIM + Banque\n\n"
        "6️⃣ Carte étudiante\n\n"
        "📞 Urgence 24/7 : +79912435421\n"
        "📲 Telegram : @Lassine223"
    )


async def nouveau_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆕 PREMIER JOUR À RUDN\n\n"
        "1. Dortoir — Installer vos affaires\n"
        "2. MFC — Enregistrement migration\n"
        "3. SNILS — Au MFC (gratuit)\n"
        "4. Gosuslugi — Créer compte\n"
        "5. Biométrie — Banque agréée\n"
        "6. SIM — MTS, Beeline, MegaFon\n"
        "7. Banque — Sberbank, carte MIR\n"
        "8. Carte étudiante — Bâtiment Principal\n\n"
        "📞 Besoin d'aide ? +79912435421"
    )


async def urgence_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 URGENCES\n\n"
        "112 — Général\n"
        "103 — Ambulance\n"
        "102 — Police\n"
        "101 — Pompiers\n\n"
        "🇲🇱 Ambassade Mali : +7 495 951 06 55\n"
        "📞 BEM-RUDN : +79912435421\n"
        "📲 @Lassine223"
    )


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


async def tickets_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Voir les tickets/questions non résolues"""
    if not est_admin(update):
        return
    tickets = fetchall("SELECT id, user_id, probleme, statut, date_creation FROM tickets WHERE statut='ouvert' OR statut='bloqué' ORDER BY id DESC LIMIT 10")
    if not tickets:
        await update.message.reply_text("Aucun ticket en attente.")
        return
    texte = "🎫 TICKETS EN ATTENTE\n\n"
    for t in tickets:
        texte += f"#{t[0]} — {t[3]} — {t[4]}\n{t[2][:100]}\n\n"
    await update.message.reply_text(texte)


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
    await update.message.reply_text("\n".join(categories[:50]) + f"\n\n... et {len(categories)-50} autres")


async def recherche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Usage : /recherche mot")
        return
    mot = " ".join(context.args)
    cle = fuzzy_search(mot, CONNAISSANCES, 50)
    if cle:
        await update.message.reply_text(CONNAISSANCES[cle])
    else:
        await update.message.reply_text("Aucune réponse trouvée. Essayez /faq")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update):
        return
    if len(context.args) == 0:
        await update.message.reply_text("Usage : /broadcast message")
        return
    message = " ".join(context.args)
    utilisateurs = fetchall("SELECT telegram_id FROM utilisateurs")
    count = 0
    for u in utilisateurs:
        try:
            await context.bot.send_message(chat_id=u[0], text="📢 BEM-RUDN\n\n" + message)
            count += 1
        except:
            pass
    await update.message.reply_text(f"Message envoyé à {count} utilisateurs.")


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
    
    # 2. Vérifier étape fait/bloqué
    etape_result = await etape_fait(update, context)
    if etape_result:
        return
    
    # 3. Vérifier urgence
    if est_urgence(message):
        enregistrer_urgence(utilisateur.id, message)
        await update.message.reply_text(message_urgence())
        return
    
    # 4. Chercher contact par nom
    contact = chercher_contact(message)
    if contact:
        await update.message.reply_text(contact)
        return
    
    # 5. FUZZY SEARCH dans connaissances
    cle = fuzzy_search(message, CONNAISSANCES, 55)
    if cle:
        await update.message.reply_text(CONNAISSANCES[cle])
        return
    
    # 6. Question non trouvée → assistance humaine
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute(
        "INSERT INTO tickets (user_id, probleme, statut, date_creation) VALUES (?, ?, 'ouvert', ?)",
        (utilisateur.id, message, now)
    )
    
    await update.message.reply_text(
        "❌ Je n'ai pas trouvé de réponse précise.\n\n"
        "📨 Votre question a été transmise au responsable BEM-RUDN.\n\n"
        "⏳ Un membre du bureau vous répondra dès que possible.\n\n"
        "📞 En cas d'urgence :\n"
        "Président : +79912697921\n"
        "Vice-président : +79912435421\n"
        "Telegram : @Lassine223"
    )


def main():
    init_database()
    initialiser_membres()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commandes étudiants
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aide", aide))
    app.add_handler(CommandHandler("membres", membres))
    app.add_handler(CommandHandler("documents", documents))
    app.add_handler(CommandHandler("dispo", dispo))
    app.add_handler(CommandHandler("parcours", parcours))
    app.add_handler(CommandHandler("arrivee", arriver_guide))
    app.add_handler(CommandHandler("nouveau", nouveau_guide))
    app.add_handler(CommandHandler("urgence", urgence_cmd))
    app.add_handler(CommandHandler("faq", faq))
    app.add_handler(CommandHandler("recherche", recherche))
    
    # Commandes admin
    app.add_handler(CommandHandler("historique", historique))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("tickets", tickets_cmd))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    # Messages texte
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texte))
    
    print("BEM-RUDN BOT démarré...")
    app.run_polling()


if __name__ == "__main__":
    main()
