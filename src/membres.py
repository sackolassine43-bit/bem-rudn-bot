from database import execute, fetchall

MEMBRES = [
    {
        "nom": "Keita Dade",
        "poste": "Président",
        "telephone": "+79912697921",
        "username": ""
    },
    {
        "nom": "Sacko Lassine",
        "poste": "Vice-président",
        "telephone": "+79912435421",
        "username": "Lassine223"
    },
    {
        "nom": "Dembelé Modibo",
        "poste": "Administration",
        "telephone": "+79918834425",
        "username": ""
    },
    {
        "nom": "Sangaré Ousmane",
        "poste": "Adjoint Administration",
        "telephone": "+79161270804",
        "username": ""
    },
    {
        "nom": "Traoré Astan B",
        "poste": "Organisation",
        "telephone": "+79164452921",
        "username": ""
    },
    {
        "nom": "Doumbia Awa",
        "poste": "Adjointe Organisation",
        "telephone": "+79303376326",
        "username": ""
    },
    {
        "nom": "Doumbia Coumba A",
        "poste": "Communication",
        "telephone": "+79569695061",
        "username": ""
    },
    {
        "nom": "Keita Fanta S",
        "poste": "Adjointe Communication",
        "telephone": "+79851981117",
        "username": ""
    },
    {
        "nom": "Thiero Hadja M",
        "poste": "Finance",
        "telephone": "+79205714407",
        "username": ""
    },
    {
        "nom": "Djiguiba Ousmane",
        "poste": "Adjoint Finance",
        "telephone": "+79919204029",
        "username": ""
    },
    {
        "nom": "Diarra Moussa K",
        "poste": "Culture",
        "telephone": "+79997120179",
        "username": ""
    },
    {
        "nom": "Touré Mohamed A",
        "poste": "Adjoint Culture",
        "telephone": "+79015976094",
        "username": ""
    },
    {
        "nom": "Fané Abdoulaye",
        "poste": "Éducation",
        "telephone": "+79773724269",
        "username": ""
    },
    {
        "nom": "Sidibé Habou",
        "poste": "Adjoint Éducation",
        "telephone": "+79694763734",
        "username": ""
    },
    {
        "nom": "Sangaré Issiaka",
        "poste": "Sport",
        "telephone": "+79999668502",
        "username": ""
    },
    {
        "nom": "Togola Boubacar A",
        "poste": "Adjoint Sport",
        "telephone": "+79996747933",
        "username": ""
    }
]


def initialiser_membres():
    membres_existants = fetchall(
        "SELECT nom FROM membres"
    )

    if membres_existants:
        return

    for membre in MEMBRES:
        execute(
            """
            INSERT INTO membres
            (
                nom,
                poste,
                telephone,
                username
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                membre["nom"],
                membre["poste"],
                membre["telephone"],
                membre["username"]
            )
        )


def get_membres():
    return fetchall(
        """
        SELECT
            nom,
            poste,
            telephone,
            disponibilite
        FROM membres
        ORDER BY poste
        """
    )


def get_membre_par_username(username):
    return fetchall(
        """
        SELECT *
        FROM membres
        WHERE username = ?
        """,
        (username,)
    )
