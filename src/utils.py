
import re
import unicodedata


def nettoyer_texte(texte):
    if not texte:
        return ""

    texte = texte.lower()

    texte = unicodedata.normalize(
        "NFD",
        texte
    )

    texte = "".join(
        c
        for c in texte
        if unicodedata.category(c) != "Mn"
    )

    texte = re.sub(
        r"[^a-z0-9\s]",
        " ",
        texte
    )

    texte = re.sub(
        r"\s+",
        " ",
        texte
    )

    return texte.strip()