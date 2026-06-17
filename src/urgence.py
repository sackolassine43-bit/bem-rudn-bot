MOTS_URGENCE = [
"urgence","urgent","aide","accident","police","malade","hopital","hôpital","perdu"
]


async def reponse_urgence(update):
    texte = """
🚨 URGENCE

Contactez immédiatement :

👤 Sacko Lassine

📞 +79912435421

Telegram :
@Lassine223
"""
    await update.message.reply_text(texte)
