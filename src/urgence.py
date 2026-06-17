from datetime import datetime

from database import execute

MOTS_URGENCE = [
    "urgence",
    "urgent",
    "accident",
    "agression",
    "danger",
    "hopital",
    "hôpital",
    "ambulance",
    "police",
    "passeport perdu",
    "visa perdu",
    "vol",
    "attaque",
]


def est_urgence(message):
    message = message.lower()

    for mot in MOTS_URGENCE:
        if mot in message:
            return True

    return False


def enregistrer_urgence(
    user_id,
    message
):
    execute(
        """
        INSERT INTO urgences
        (
            user_id,
            message,
            niveau,
            date_creation
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            message,
            "élevé",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )


def message_urgence():
    return """
🚨 URGENCE

112 : Urgence générale
101 : Pompiers
102 : Police
103 : Ambulance

🇲🇱 Ambassade du Mali :
+7 495 951 06 55
"""