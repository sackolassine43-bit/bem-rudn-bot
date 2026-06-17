from datetime import datetime

from database import execute, fetchall


def enregistrer_message(
    telegram_id,
    nom,
    message
):
    execute(
        """
        INSERT INTO historique
        (
            telegram_id,
            nom,
            message,
            date_message
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            telegram_id,
            nom,
            message,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )


def get_historique(limit=100):
    return fetchall(
        f"""
        SELECT
            nom,
            message,
            date_message
        FROM historique
        ORDER BY id DESC
        LIMIT {limit}
        """
    )


def total_messages():
    resultat = fetchall(
        """
        SELECT COUNT(*)
        FROM historique
        """
    )

    return resultat[0][0] if resultat else 0
