import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = "8885232569:AAFz5WQLXSgTKrsTlziJM8xiuE2VULJu_aM"
DATABASE_NAME = os.getenv("DATABASE_NAME", "data/bem_rudn.db")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "Lassine223")
FUZZY_THRESHOLD = 55

VP_ID = "+79912435421"
PRESIDENT_ID = "+79912697921"

MEMBRES_BUREAU = {
    "+79912697921": {"nom": "Keita Dade", "poste": "Président", "pole": "Direction", "role": "president", "telegram": ""},
    "+79912435421": {"nom": "Sacko Lassine", "poste": "Vice-Président", "pole": "Direction", "role": "vice_president", "telegram": "@Lassine223"},
    "+79918834425": {"nom": "Dembelé Modibo", "poste": "Responsable", "pole": "Administration", "role": "responsable", "telegram": ""},
    "+79161270804": {"nom": "Sangaré Ousmane", "poste": "Adjoint", "pole": "Administration", "role": "adjoint", "telegram": ""},
    "+79164452921": {"nom": "Traoré Astan B", "poste": "Responsable", "pole": "Organisation", "role": "responsable", "telegram": ""},
    "+79303376326": {"nom": "Doumbia Awa", "poste": "Adjointe", "pole": "Organisation", "role": "adjoint", "telegram": ""},
    "+79569695061": {"nom": "Doumbia Coumba A", "poste": "Responsable", "pole": "Communication", "role": "responsable", "telegram": ""},
    "+79851981117": {"nom": "Keita Fanta S", "poste": "Adjointe", "pole": "Communication", "role": "adjoint", "telegram": ""},
    "+79205714407": {"nom": "Thiero Hadja M", "poste": "Responsable", "pole": "Finance", "role": "responsable", "telegram": ""},
    "+79919204029": {"nom": "Djiguiba Ousmane", "poste": "Adjoint", "pole": "Finance", "role": "adjoint", "telegram": ""},
    "+79997120179": {"nom": "Diarra Moussa K", "poste": "Responsable", "pole": "Culture", "role": "responsable", "telegram": ""},
    "+79015976094": {"nom": "Touré Mohamed A", "poste": "Adjoint", "pole": "Culture", "role": "adjoint", "telegram": ""},
    "+79773724269": {"nom": "Fané Abdoulaye", "poste": "Responsable", "pole": "Éducation", "role": "responsable", "telegram": ""},
    "+79694763734": {"nom": "Sidibé Habou", "poste": "Adjoint", "pole": "Éducation", "role": "adjoint", "telegram": ""},
    "+79999668502": {"nom": "Sangaré Issiaka", "poste": "Responsable", "pole": "Sport", "role": "responsable", "telegram": ""},
    "+79996747933": {"nom": "Togola Boubacar A", "poste": "Adjoint", "pole": "Sport", "role": "adjoint", "telegram": ""},
}

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

ETATS_DISPONIBILITE = ["disponible", "occupé", "absent"]
VERSION = "1.0.0"
PROJECT_NAME = "BEM-RUDN BOT"
