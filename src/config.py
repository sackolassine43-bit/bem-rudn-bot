import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "data/bem_rudn.db"
)

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "Lassine223"
)

RUDN_INFO = {
    "universite": "RUDN University",
    "adresse": "117198 Moscou, 6 rue Miklukho-Maklaya",
    "telephone": "+7 (499) 936-87-87",
    "email": "mfc@rudn.ru",
}

ADMISSION_INFO = {
    "adresse": "10/2 rue Miklukho-Maklaya, Moscou",
    "telephone": "+7 (499) 936-86-94",
    "email": "intstudent@rudn.ru",
}

MFC_INFO = {
    "adresse": "6 rue Miklukho-Maklaya, Rez-de-chaussée",
    "horaires": "09h00 - 18h00",
    "email": "mfc@rudn.ru",
}

LOGEMENT_INFO = {
    "email": "accomodation@rudn.ru",
    "telephone": "+7 (499) 936-87-64",
}

AMBASSADE_MALI = {
    "adresse": "Novokuznetskaya 11, 115184 Moscou",
    "telephone_1": "+7 495 951 06 55",
    "telephone_2": "+7 495 951 27 84",
    "email": "amaliru@mail.ru",
}

URGENCES = {
    "112": "Urgence générale",
    "101": "Pompiers",
    "102": "Police",
    "103": "Ambulance",
}

ETATS_DISPONIBILITE = [
    "disponible",
    "occupé",
    "absent"
]

FUZZY_THRESHOLD = 60

VERSION = "1.0.0"
PROJECT_NAME = "BEM-RUDN BOT"
