from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
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
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
HEURES = ["Matin (8h-12h)", "Après-midi (12h-18h)", "Soir (18h-22h)", "Journée (8h-18h)"]


def est_admin(update):
    u = update.effective_user
    return u.username and u.username.lower() == ADMIN_USERNAME.lower()


def fuzzy_search(query, connaissances, threshold=55):
    best_score, best_key = 0, None
    query = query.lower().strip()
    for key in connaissances:
        score = fuzz.ratio(query, key.lower())
        if score > best_score:
            best_score, best_key = score, key
    return best_key if best_score >= threshold else None


def chercher_contact(message):
    msg = message.lower()
    for tel, infos in MEMBRES_BUREAU.items():
        if infos["nom"].lower() in msg:
            return f"👤 {infos['nom']} — {infos['poste']} {infos['pole']}\n📞 {tel}"
    msg_clean = ''.join(c for c in unicodedata.normalize('NFD', msg) if unicodedata.category(c) != 'Mn')
    for tel, infos in MEMBRES_BUREAU.items():
        nom_clean = ''.join(c for c in unicodedata.normalize('NFD', infos["nom"].lower()) if unicodedata.category(c) != 'Mn')
        if nom_clean in msg_clean:
            return f"👤 {infos['nom']} — {infos['poste']} {infos['pole']}\n📞 {tel}"
    for tel, infos in MEMBRES_BUREAU.items():
        prenom = infos["nom"].split()[0].lower()
        prenom_clean = ''.join(c for c in unicodedata.normalize('NFD', prenom) if unicodedata.category(c) != 'Mn')
        if prenom_clean in msg_clean:
            return f"👤 {infos['nom']} — {infos['poste']} {infos['pole']}\n📞 {tel}"
    return None


# ==================== COMMANDES ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    execute("INSERT OR IGNORE INTO utilisateurs (telegram_id, nom, username, date_inscription) VALUES (?, ?, ?, datetime('now'))", (u.id, u.full_name, u.username))
    await update.message.reply_text(
        "🇲🇱 BEM-RUDN 2026-2027\nBureau des Étudiants Maliens de RUDN\nUnité - Solidarité - Excellence\n\n"
        "👋 Bienvenue ! Écrivez votre question :\n"
        "• visa • dortoir • banque • SIM • admission\n"
        "• aéroport • médical • contact...\n\n"
        "📌 /start /aide /parcours /dispo /arrivee /nouveau /urgence"
    )

async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 /start /aide /parcours /dispo /arrivee /nouveau /urgence\n"
        "/membres /documents /faq /recherche mot /signaler"
    )

async def membres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lignes = [f"{m[1]}\n{m[0]}\n{m[2]}\n{m[3]}" for m in get_membres()]
    await update.message.reply_text("\n\n".join(lignes))

async def documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_documents("all"))

async def dispo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_disponibilites())

async def parcours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = "📋 LES 7 ÉTAPES\n\n"
    for num, etape in ETAPES.items():
        texte += f"{num}. {etape}\n"
    texte += "\n📌 étape 1 fait\n📌 bloqué étape 3"
    await update.message.reply_text(texte)

async def etape_fait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower().strip()
    u = update.effective_user
    if msg.startswith("étape ") and "fait" in msg:
        try:
            num = int(msg.replace("étape ", "").replace(" fait", "").strip())
            if 1 <= num <= 7:
                execute("INSERT OR IGNORE INTO etudiants (telegram_id, nom, etape) VALUES (?, ?, ?)", (u.id, u.full_name, num))
                execute("UPDATE etudiants SET etape=?, date_modification=datetime('now') WHERE telegram_id=?", (num, u.id))
                await update.message.reply_text(f"✅ Étape {num} validée : {get_etape(num)}")
                return True
        except: pass
    if msg.startswith("bloqué étape "):
        try:
            num = int(msg.replace("bloqué étape ", "").strip())
            execute("INSERT INTO tickets (user_id, probleme, statut, date_creation) VALUES (?, ?, 'bloqué', ?)", (u.id, f"Bloqué étape {num}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            await update.message.reply_text(f"🔴 ALERTE — Bloqué étape {num}.\n📞 +79912435421")
            return True
        except: pass
    return None

async def arriver_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛬 GUIDE ARRIVANT\n\n1. Aéroport → RUDN (Aeroexpress + métro)\n"
        "2. Dortoir : 15 rue Miklukho-Maklaya, Bât.1, Salle 2\n"
        "3. MFC RUDN (RdC, 9h-18h)\n4. Centre médical\n5. SIM + Banque\n6. Carte étudiante\n\n📞 +79912435421"
    )

async def nouveau_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆕 PREMIER JOUR\n\n1. Dortoir\n2. MFC\n3. SNILS\n4. Gosuslugi\n5. Biométrie\n"
        "6. SIM\n7. Banque MIR\n8. Carte étudiante\n\n📞 +79912435421"
    )

async def urgence_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚨 112 Général | 103 Ambulance | 102 Police | 101 Pompiers\n🇲🇱 Ambassade : +7 495 951 06 55\n📞 BEM-RUDN : +79912435421")

async def signaler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage : /signaler description")
        return
    execute("INSERT INTO signalements (user_id, message, date_creation) VALUES (?, ?, ?)", (update.effective_user.id, " ".join(context.args), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    await update.message.reply_text("✅ Signalement enregistré.")

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
    tickets = fetchall("SELECT id, probleme, statut, date_creation FROM tickets WHERE statut IN ('ouvert','bloqué') ORDER BY id DESC LIMIT 10")
    if not tickets:
        await update.message.reply_text("Aucun ticket.")
        return
    texte = "🎫 TICKETS\n\n"
    for t in tickets:
        texte += f"#{t[0]} [{t[2]}] {t[3]}\n{t[1][:100]}\n\n"
    await update.message.reply_text(texte)

async def repondre_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
    if len(context.args) < 2:
        await update.message.reply_text("Usage : /repondre numero message")
        return
    try:
        tid = int(context.args[0])
        reponse = " ".join(context.args[1:])
        ticket = fetchone("SELECT user_id FROM tickets WHERE id=?", (tid,))
        if not ticket:
            await update.message.reply_text("Ticket introuvable.")
            return
        await context.bot.send_message(chat_id=ticket[0], text=f"📨 BEM-RUDN :\n\n{reponse}")
        execute("UPDATE tickets SET statut='résolu' WHERE id=?", (tid,))
        await update.message.reply_text(f"✅ Ticket #{tid} résolu.")
    except:
        await update.message.reply_text("Erreur.")

async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
    from admin import sauvegarder_base
    await update.message.reply_document(open(sauvegarder_base(), "rb"))

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
    await update.message.reply_text("🔐 /stats /historique /backup /broadcast /tickets")

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cats = sorted(CONNAISSANCES.keys())
    await update.message.reply_text("\n".join(cats[:50]) + f"\n\n+ {len(cats)-50} autres")

async def recherche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage : /recherche mot")
        return
    mot = " ".join(context.args)
    cle = fuzzy_search(mot, CONNAISSANCES, 50)
    await update.message.reply_text(CONNAISSANCES.get(cle, "Aucune réponse. Essayez /faq"))

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not est_admin(update): return
    if not context.args:
        await update.message.reply_text("Usage : /broadcast message")
        return
    msg = " ".join(context.args)
    users = fetchall("SELECT telegram_id FROM utilisateurs")
    count = sum(1 for u in users if not (lambda: None, await context.bot.send_message(chat_id=u[0], text="📢 BEM-RUDN\n\n"+msg))[0])
    await update.message.reply_text(f"Envoyé à {count} utilisateurs.")


# ==================== MENU DISPO INTERACTIF ====================
async def menu_dispo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    membre = None
    for tel, infos in MEMBRES_BUREAU.items():
        if u.username and u.username.lower() == infos.get("telegram", "").lower().replace("@", ""):
            membre = infos
            break
    if not membre:
        await update.message.reply_text("❌ Réservé aux membres du bureau.")
        return
    keyboard = [[InlineKeyboardButton(j, callback_data=f"jour_{j}")] for j in JOURS]
    await update.message.reply_text(f"📅 {membre['nom']}, choisissez un jour :", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("jour_"):
        jour = data.replace("jour_", "")
        context.user_data["jour"] = jour
        keyboard = [[InlineKeyboardButton(h, callback_data=f"heure_{h}")] for h in HEURES]
        keyboard.append([InlineKeyboardButton("❌ Absent", callback_data="absent_jour")])
        await query.edit_message_text(f"📅 {jour} — Horaires :", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("heure_"):
        heure = data.replace("heure_", "")
        jour = context.user_data.get("jour", "")
        u = query.from_user
        for tel, infos in MEMBRES_BUREAU.items():
            if u.username and u.username.lower() == infos.get("telegram", "").lower().replace("@", ""):
                execute("UPDATE membres SET disponibilite='disponible', horaires=? WHERE nom=?", (f"{jour} {heure}", infos["nom"]))
                break
        await query.edit_message_text(f"✅ {jour} — {heure}")
    elif data == "absent_jour":
        await query.edit_message_text(f"✅ Absent le {context.user_data.get('jour', '')}")


# ==================== DISPONIBILITÉS ====================
async def gerer_dispo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    msg = update.message.text.lower().strip()
    membre = None
    for tel, infos in MEMBRES_BUREAU.items():
        if u.username and u.username.lower() == infos.get("telegram", "").lower().replace("@", ""):
            membre = infos
            break
    if not membre:
        return None
    if msg == "dispo":
        await menu_dispo(update, context)
        return True
    if msg == "absent":
        execute("UPDATE membres SET disponibilite='absent', horaires='' WHERE nom=?", (membre["nom"],))
        await update.message.reply_text(f"✅ {membre['nom']} — Absent")
        return True
    if msg in ["occupé", "occupe"]:
        execute("UPDATE membres SET disponibilite='occupe' WHERE nom=?", (membre["nom"],))
        await update.message.reply_text(f"✅ {membre['nom']} — Occupé")
        return True
    if msg == "dispo journée":
        execute("UPDATE membres SET disponibilite='disponible', horaires='9h-18h' WHERE nom=?", (membre["nom"],))
        await update.message.reply_text(f"✅ {membre['nom']} — Disponible journée")
        return True
    if msg.startswith("dispo "):
        h = msg.replace("dispo ", "").strip()
        execute("UPDATE membres SET disponibilite='disponible', horaires=? WHERE nom=?", (h, membre["nom"]))
        await update.message.reply_text(f"✅ {membre['nom']} — {h}")
        return True
    return None


# ==================== NOTIFICATION ====================
async def notifier_membre_disponible(update: Update, context, question):
    membres_dispos = fetchall("SELECT nom, username FROM membres WHERE disponibilite='disponible' LIMIT 1")
    if membres_dispos:
        nom, username = membres_dispos[0]
        # Essayer via username Telegram
        if username and username.startswith("@"):
            try:
                await context.bot.send_message(
                    chat_id=username,
                    text=f"📨 Question d'un étudiant :\n\n{question}\n\n📌 Répondre : /repondre"
                )
                await update.message.reply_text(
                    f"📨 Votre question a été transmise à {nom} (membre disponible).\n⏳ Patientez."
                )
                return
            except:
                pass
    
    # Fallback : envoyer au VP
    try:
        await context.bot.send_message(
            chat_id="@Lassine223",
            text=f"📨 Question sans réponse :\n\n{question}\n\n(Aucun membre joignable)"
        )
        await update.message.reply_text(
            "📨 Question transmise au Vice-Président.\n⏳ Patientez.\n\n📞 +79912435421"
        )
        return
    except:
        pass
    
    await update.message.reply_text("❌ Aucun membre disponible.\n📞 +79912435421")


# ==================== MESSAGES TEXTE ====================
async def texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    msg = update.message.text
    enregistrer_message(u.id, u.full_name, msg)
    if await gerer_dispo(update, context): return
    if await etape_fait(update, context): return
    contact = chercher_contact(msg)
    if contact:
        await update.message.reply_text(contact)
        return
    if est_urgence(msg):
        enregistrer_urgence(u.id, msg)
        await update.message.reply_text(message_urgence())
        return
    cle = fuzzy_search(msg, CONNAISSANCES, 55)
    if cle:
        await update.message.reply_text(CONNAISSANCES[cle])
        return
    for mot_cle, reponse in CONNAISSANCES.items():
        if mot_cle in msg.lower():
            await update.message.reply_text(reponse)
            return
    await notifier_membre_disponible(update, context, msg)


def main():
    init_database()
    initialiser_membres()
    app = Application.builder().token(BOT_TOKEN).build()
    for cmd, func in [("start", start), ("aide", aide), ("membres", membres), ("documents", documents),
                       ("dispo", dispo), ("parcours", parcours), ("arrivee", arriver_guide),
                       ("nouveau", nouveau_guide), ("urgence", urgence_cmd), ("faq", faq),
                       ("recherche", recherche), ("signaler", signaler), ("historique", historique),
                       ("stats", stats), ("tickets", tickets_cmd), ("repondre", repondre_ticket),
                       ("backup", backup), ("panel", panel), ("broadcast", broadcast)]:
        app.add_handler(CommandHandler(cmd, func))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texte))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("✅ BEM-RUDN en ligne !")
    app.run_polling()


if __name__ == "__main__":
    main()
