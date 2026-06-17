from rapidfuzz import fuzz

from config import FUZZY_THRESHOLD
from utils import nettoyer_texte


def score(question, mot_cle):
    question = nettoyer_texte(question)
    mot_cle = nettoyer_texte(mot_cle)

    return fuzz.ratio(
        question,
        mot_cle
    )


def correspond(question, mot_cle):
    return score(
        question,
        mot_cle
    ) >= FUZZY_THRESHOLD


def meilleur_match(
    question,
    liste_mots
):
    meilleur_score = 0
    meilleur_mot = None

    for mot in liste_mots:
        s = score(
            question,
            mot
        )

        if s > meilleur_score:
            meilleur_score = s
            meilleur_mot = mot

    return (
        meilleur_mot,
        meilleur_score
    )
