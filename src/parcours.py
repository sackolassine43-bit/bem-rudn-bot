ETAPES = {
    1: "Arrivée à Moscou",
    2: "Dortoir provisoire",
    3: "Enregistrement migration",
    4: "Analyses médicales",
    5: "Carte étudiante",
    6: "Banque",
    7: "Carte SIM"
}


def get_etape(numero):
    return ETAPES.get(
        numero,
        "Étape inconnue"
    )


def parcours_complet():
    texte = ""

    for numero, etape in ETAPES.items():
        texte += f"{numero}. {etape}\n"

    return texte