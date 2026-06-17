from datetime import datetime

from database import (
    execute,
    fetchall
)


def definir_disponibilite(
    username,
    etat,
    horaires=""
):
    execute(
        """
        UPDATE membres
        SET disponibilite = ?,
            horaires = ?
        WHERE username = ?
        """,
        (
            etat,
            horaires,
            username
        )
    )

    execute(
        """
        INSERT INTO disponibilites
        (
            membre_id,
            etat,
            horaires,
            date_modification
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            0,
            etat,
            horaires,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )


def toutes_disponibilites():
    return fetchall(
        """
        SELECT
            nom,
            poste,
            disponibilite,
            horaires
        FROM membres
        ORDER BY poste
        """
    )


def format_disponibilites():
    lignes = []

    for membre in toutes_disponibilites():
        nom, poste, dispo, horaires = membre

        ligne = (
            f"{poste}\n"
            f"{nom}\n"
            f"{dispo}"
        )

        if horaires:
            ligne += f" ({horaires})"

        lignes.append(ligne)

    return "\n\n".join(lignes)