LICENCE = """
Licence :

• Passeport
• Bac
• Relevés du Bac
• Traductions
• Légalisations
"""

MASTER = """
Master :

• Passeport
• Diplôme Licence
• Relevés Licence
• Traductions
• Légalisations
"""

DOCTORAT = """
Doctorat :

• Passeport
• Diplôme Master
• Relevés Master
• Traductions
• Légalisations
"""


def get_documents(niveau):
    niveau = niveau.lower()

    if "licence" in niveau:
        return LICENCE

    if "master" in niveau:
        return MASTER

    if "doctorat" in niveau:
        return DOCTORAT

    return (
        LICENCE
        + "\n\n"
        + MASTER
        + "\n\n"
        + DOCTORAT
    )