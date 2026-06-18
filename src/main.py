from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
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
import unicodedata

ADMIN_USERNAME = "Lassine223"


def est_admin(update):
    utilisateur = update.effective_user
    return utilisateur.username and utilisateur.username.lower() == ADMIN_USERNAME.lower()


def fuzzy_search(query, connaissances, threshold=55):
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


def chercher_contact(message):
    """Cherche un membre du bureau par son nom - PRIORITÉ ABSOLUE"""
    message_lower = message.lower()
    
    # 1. Correspondance exacte
    for tel, infos in MEMBRES_BUREAU.items():
        if infos["nom"].lower() in message_lower:
            return f"👤 {infos['nom']} — {infos['poste']} {infos['pole']}\n📞 {tel}"
    
    # 2. Correspondance sans accents
    message_clean = ''.join(c for c in unicodedata.normalize('NFD', message_lower) if unicodedata.category(c) != 'Mn')
    for tel, infos in MEMBRES_BUREAU.items():
        nom_clean = ''.join(c for c in unicodedata.normalize('NFD', infos["nom"].lower()) if unicodedata.category(c) != 'Mn')
        if nom_clean in message_clean:
            return f"👤 {infos['nom']} — {infos['poste']} {infos['pole']}\n📞 {tel}"
    
    # 3. Correspondance par prénom seul
    for tel, infos in MEMBRES_BUREAU.items():
        prenom = infos["nom"].split()[0].lower()
        prenom_clean = ''.join(c for c in unicodedata.normalize('NFD', prenom) if unicodedata.category(c) != 'Mn')
        if prenom_clean in message_clean:
            return f"👤 {infos['nom']} — {infos['poste']} {infos['pole']}\n📞 {tel}"
    
    return None


# ==================== COMMANDES ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utilisateur = update.effective_user
    execute("INSERT OR IGNORE INTO utilisateurs (telegram_id, nom, username, date_inscription) VALUES (?, ?, ?, datetime('now'))", (utilisateur.id, utilisateur.full_name, utilisateur.username))
    await update.message.reply_text(
        "🇲🇱 BEM-RUDN 2026-2027\nBureau des Étudiants Maliens de RUDN\nUnité - Solidarité - Excellence\n\n"
        "👋 Bienvenue ! Je suis votre assistant.\n\n"
        "✍️ Écrivez simplement votre question :\n"
        "• visa\n• dortoir\n• banque\n• SIM\n• admission\n• aéroport\n• médical\n• contact...\n\n"
        "📌 Commandes utiles :\n"
        "/start - Accueil\n/aide - Toutes les commandes\n/parcours - Les 7 étapes\n"
        "/dispo - Bureau disponible\n/arrivee - Guide arrivant\n/nouveau - Premier jour\n"
        "/urgence - Numéros d'urgence\n\n🇲🇱 Le Mali, une seule famille !"
    )


async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 COMMANDES ÉTUDIANTS\n/start - Accueil\n/aide - Cette liste\n/parcours - Voir les 7 étapes\n"
        "/dispo - Disponibilités bureau\n/arrivee - Guide nouvel arrivant\n/nouveau - Guide premier jour\n"
        "/urgence - Contacts urgence\n/membres - Liste du bureau\n/documents - Documents par niveau\n"
        "/faq - Tous les sujets\n/recherche mot - Chercher\n/signaler - Signaler une erreur"
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
    texte += "\n📌 Validez : étape 1 fait\n📌 Bloqué : bloqué étape 3"
    await update.message.reply_text(texte)


async def etape_fait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower().strip()
    utilisateur = update.effective_user
    if message.startswith("étape ") and "fait" in message:
        try:
            num = int(message.replace("étape ", "").replace(" fait", "").strip())
            if 1 <= num <= 7:
                execute("INSERT OR IGNORE INTO etudiants (telegram_id, nom, etape) VALUES (?, ?, ?)", (utilisateur.id, utilisateur.full_name, num))
                execute("UPDATE etudiants SET etape=?, date_modification=datetime('now') WHERE telegram_id=?", (num, utilisateur.id))
                await update.message.reply_text(f"✅ Étape {num} validée : {get_etape(num)}")
                return True
        except: pass
    if message.startswith("bloqué étape "):
        try:
            num = int(message.replace("bloqué étape ", "").strip())
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            execute("INSERT INTO tickets (user_id, probleme, statut, date_creation) VALUES (?, ?, 'bloqué', ?)", (utilisateur.id, f"Étudiant bloqué à l'étape {num}", now))
            await update.message.reply_text(f"🔴 ALERTE — Bloqué à l'étape {num}.\nUn responsable BEM-RUDN va vous contacter.\n📞 Urgence : +79912435421")
            return True
        except: pass
    return None


async def arriver_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛬 GUIDE NOUVEL ARRIVANT\n\n1️⃣ Aéroport → Campus RUDN\n   Aeroexpress + métro ou Yandex Go\n\n"
        "2️⃣ Dortoir provisoire\n   15 rue Miklukho-Maklaya, Bât.1, Salle 2\n\n"
        "3️⃣ MFC RUDN (RdC, 9h-18h)\n   Enregistrement migration\n\n"
        "4️⃣ Centre médical\n   10 rue Miklukho-Maklaya\n\n5️⃣ Carte SIM + Banque\n\n6️⃣ Carte étudiante\n\n"
        "📞 Urgence : +79912435421\n📲 @Lassine223"
    )


async def nouveau_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆕 PREMIER JOUR À RUDN\n\n1. Dortoir — Installer vos affaires\n2. MFC — Enregistrement migration\n"
        "3. SNILS — Au MFC (gratuit)\n4. Gosuslugi — Créer compte\n5. Biométrie — Banque agréée\n"
        "6. SIM — MTS, Beeline, MegaFon\n7. Banque — Sberbank, carte MIR\n8. Carte étudiante — Bâtiment Principal\n\n"
        "📞 Besoin d'aide ? +79912435421"
    )


async def urgence_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 URGENCES\n\n112 — Général\n103 — Ambulance\n102 — Police\n101 — Pompiers\n\n"
        "🇲🇱 Ambassade Mali : +7 495 951 06 55\n📞 BEM-RUDN : +79912435421\n📲 @Lassine223"
    )


async def signaler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Usage : /signaler description")
        return
    message = " ".join(context.args)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute("INSERT INTO signalements (user_id, message, date_creation) VALUES (?, ?, ?)", (update.effective_user.id, message, now))
    await update.message.reply_text("✅ Signalement enregistré. Merci !")


# ==================== ADMIN ====================
async def historique(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
    from admin import historique_admin
    await update.message.reply_text(historique_admin(50))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
    from admin import statistiques
    await update.message.reply_text(statistiques())


async def tickets_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
    tickets = fetchall("SELECT id, user_id, probleme, statut, date_creation FROM tickets WHERE statut='ouvert' OR statut='bloqué' ORDER BY id DESC LIMIT 10")
    if not tickets:
        await update.message.reply_text("Aucun ticket en attente.")
        return
    texte = "🎫 TICKETS EN ATTENTE\n\n"
    for t in tickets:
        texte += f"#{t[0]} — {t[3]} — {t[4]}\n{t[2][:100]}\n\n"
    await update.message.reply_text(texte)


async def repondre_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
    if len(context.args) < 2:
        await update.message.reply_text("Usage : /repondre numero message")
        return
    try:
        ticket_id = int(context.args[0])
        reponse = " ".join(context.args[1:])
        ticket = fetchone("SELECT user_id FROM tickets WHERE id=?", (ticket_id,))
        if not ticket:
            await update.message.reply_text("Ticket introuvable.")
            return
        await context.bot.send_message(chat_id=ticket[0], text=f"📨 Réponse BEM-RUDN :\n\n{reponse}")
        execute("UPDATE tickets SET statut='résolu' WHERE id=?", (ticket_id,))
        await update.message.reply_text(f"✅ Ticket #{ticket_id} résolu.")
    except:
        await update.message.reply_text("Erreur.")


async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
    from admin import sauvegarder_base
    fichier = sauvegarder_base()
    await update.message.reply_document(open(fichier, "rb"))


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
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
        await update.message.reply_text("Aucune réponse. Essayez /faq")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
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
        except: pass
    await update.message.reply_text(f"Message envoyé à {count} utilisateurs.")


# ==================== DISPONIBILITÉS ====================
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
        await update.message.reply_text(f"✅ {membre['nom']} — Disponible toute la journée")
        return True
    if message.startswith("dispo ") and not message.startswith("dispo journée"):
        horaires = message.replace("dispo ", "").strip()
        execute("UPDATE membres SET disponibilite='disponible', horaires=? WHERE nom=?", (horaires, membre["nom"]))
        await update.message.reply_text(f"✅ {membre['nom']} — Disponible : {horaires}")
        return True
    if message == "dispo":
        await menu_dispo(update, context)
        return True
    
    if message == "dispo":
        result = fetchone("SELECT disponibilite, horaires FROM membres WHERE nom=?", (membre["nom"],))
        if result:
            etat, horaires = result
            await update.message.reply_text(f"👤 {membre['nom']} — {membre['poste']}\nStatut : {etat}\nHoraires : {horaires or 'Non défini'}")
        return True
    return None


# ==================== MESSAGES TEXTE ====================
async def texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utilisateur = update.effective_user
    message = update.message.text
    enregistrer_message(utilisateur.id, utilisateur.full_name, message)
    
    # 1. PRIORITÉ ABSOLUE : Disponibilité membre
    dispo_result = await gerer_dispo(update, context)
    if dispo_result: return
    
    # 2. PRIORITÉ ABSOLUE : Contact par nom
    contact = chercher_contact(message)
    if contact:
        await update.message.reply_text(contact)
        return
    
    # 3. Étape fait/bloqué
    etape_result = await etape_fait(update, context)
    if etape_result: return
    
    # 4. Urgence
    if est_urgence(message):
        enregistrer_urgence(utilisateur.id, message)
        await update.message.reply_text(message_urgence())
        return
    
    # 5. Fuzzy search
    cle = fuzzy_search(message, CONNAISSANCES, 55)
    if cle:
        await update.message.reply_text(CONNAISSANCES[cle])
        return
    
    # 6. Recherche exacte
    message_min = message.lower()
    for mot_cle, reponse in CONNAISSANCES.items():
        if mot_cle in message_min:
            await update.message.reply_text(reponse)
            return
    
    # 7. Assistance humaine → notifier membre disponible
    await notifier_membre_disponible(update, context, message)


def main():
    init_database()
    initialiser_membres()
    app = Application.builder().token(BOT_TOKEN).build()
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
    app.add_handler(CommandHandler("signaler", signaler))
    app.add_handler(CommandHandler("historique", historique))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("tickets", tickets_cmd))
    app.add_handler(CommandHandler("repondre", repondre_ticket))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texte))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("✅ BEM-RUDN 2026-2027 en ligne !")
    app.run_polling()


if __name__ == "__main__":
    main()

# ==================== NOTIFICATION MEMBRE DISPONIBLE ====================
async def notifier_membre_disponible(context, user_id, question):
    """Envoie la question à un membre du bureau disponible"""
    membres_dispos = fetchall(
        "SELECT nom, telephone, telegram_id FROM membres WHERE disponibilite='disponible' LIMIT 1"
    )
    
    if membres_dispos:
        nom, tel, telegram_id = membres_dispos[0]
        try:
            await context.bot.send_message(
                chat_id=telegram_id or user_id,
                text=f"📨 Nouvelle question d'un étudiant :\n\n{question}\n\n/répondre à cet étudiant"
            )
            return True
        except:
            pass
    
    # Si personne dispo → envoyer au VP
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📨 Question sans réponse (aucun membre disponible) :\n\n{question}"
        )
    except:
        pass
    return False

# ==================== NOTIFICATION MEMBRE DISPONIBLE ====================
async def notifier_membre_disponible(update, context, question):
    """Envoie la question au premier membre du bureau disponible"""
    membres_dispos = fetchall(
        "SELECT nom, telegram_id FROM membres WHERE disponibilite='disponible' LIMIT 1"
    )
    
    if membres_dispos:
        nom, telegram_id = membres_dispos[0]
        if telegram_id:
            try:
                await context.bot.send_message(
                    chat_id=telegram_id,
                    text=f"📨 Question d'un étudiant :\n\n{question}\n\n📌 Répondre : /repondre"
                )
                await update.message.reply_text(
                    "📨 Votre question a été transmise à un membre disponible du bureau.\n"
                    "⏳ Vous recevrez une réponse bientôt."
                )
                return
            except:
                pass
    
    # Fallback : envoyer au VP
    await update.message.reply_text(
        "❌ Aucun membre du bureau n'est disponible actuellement.\n\n"
        "📞 Contactez directement le Vice-Président :\n"
        "📞 +79912435421\n📲 @Lassine223"
    )

# ==================== NOTIFICATION MEMBRE DISPONIBLE ====================
async def notifier_membre_disponible(update, context, question):
    membres_dispos = fetchall(
        "SELECT nom, telegram_id FROM membres WHERE disponibilite='disponible' LIMIT 1"
    )
    
    if membres_dispos:
        nom, telegram_id = membres_dispos[0]
        if telegram_id:
            try:
                await context.bot.send_message(
                    chat_id=telegram_id,
                    text=f"📨 Question d'un étudiant :\n\n{question}\n\n📌 Répondre : /repondre"
                )
                await update.message.reply_text(
                    "📨 Votre question a été transmise à un membre disponible du bureau.\n"
                    "⏳ Vous recevrez une réponse bientôt."
                )
                return
            except:
                pass
    
    await update.message.reply_text(
        "❌ Aucun membre du bureau n'est disponible actuellement.\n\n"
        "📞 Contactez directement le Vice-Président :\n"
        "📞 +79912435421\n📲 @Lassine223"
    )

# ==================== MENU DISPONIBILITÉS INTERACTIF ====================
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
HEURES = ["Matin (8h-12h)", "Après-midi (12h-18h)", "Soir (18h-22h)", "Journée (8h-18h)"]

async def menu_dispo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche le menu interactif des disponibilités"""
    utilisateur = update.effective_user
    membre = None
    for tel, infos in MEMBRES_BUREAU.items():
        if utilisateur.username and utilisateur.username.lower() == infos.get("telegram", "").lower().replace("@", ""):
            membre = infos
            break
    
    if not membre:
        await update.message.reply_text("❌ Cette commande est réservée aux membres du bureau.")
        return
    
    keyboard = []
    for i in range(0, len(JOURS), 2):
        row = [InlineKeyboardButton(JOURS[j], callback_data=f"jour_{JOURS[j]}") for j in range(i, min(i+2, len(JOURS)))]
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"📅 {membre['nom']}, choisissez un jour de disponibilité :",
        reply_markup=reply_markup
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur les boutons"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("jour_"):
        jour = data.replace("jour_", "")
        context.user_data["jour_choisi"] = jour
        
        keyboard = []
        for h in HEURES:
            keyboard.append([InlineKeyboardButton(h, callback_data=f"heure_{h}")])
        keyboard.append([InlineKeyboardButton("❌ Absent ce jour", callback_data="absent_jour")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"📅 Jour : {jour}\nChoisissez vos horaires :",
            reply_markup=reply_markup
        )
    
    elif data.startswith("heure_"):
        heure = data.replace("heure_", "")
        jour = context.user_data.get("jour_choisi", "")
        utilisateur = query.from_user
        
        membre = None
        for tel, infos in MEMBRES_BUREAU.items():
            if utilisateur.username and utilisateur.username.lower() == infos.get("telegram", "").lower().replace("@", ""):
                membre = infos
                break
        
        if membre:
            execute(
                "UPDATE membres SET disponibilite='disponible', horaires=? WHERE nom=?",
                (f"{jour} {heure}", membre["nom"])
            )
        
        await query.edit_message_text(f"✅ Disponibilité enregistrée :\n📅 {jour}\n🕐 {heure}")
    
    elif data == "absent_jour":
        jour = context.user_data.get("jour_choisi", "")
        await query.edit_message_text(f"✅ Marqué absent le {jour}")

