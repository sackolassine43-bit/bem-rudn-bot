from rapidfuzz import fuzz


def trouver_question(message, connaissances):
    meilleur_score = 0
    meilleure_reponse = None
    for mot, reponse in connaissances.items():
        score = fuzz.ratio(message.lower(), mot.lower())
        if score > meilleur_score:
            meilleur_score = score
            meilleure_reponse = reponse
    if meilleur_score >= 60:
        return meilleure_reponse
    return None
