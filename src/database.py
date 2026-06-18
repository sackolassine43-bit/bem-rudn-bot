import sqlite3
from pathlib import Path

from config import DATABASE_NAME


def get_connection():
    Path("data").mkdir(exist_ok=True)
    return sqlite3.connect(DATABASE_NAME)


def init_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS utilisateurs (
        telegram_id INTEGER PRIMARY KEY,
        nom TEXT,
        username TEXT,
        date_inscription TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS historique (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        nom TEXT,
        message TEXT,
        date_message TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS membres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        poste TEXT NOT NULL,
        telephone TEXT,
        username TEXT,
        telegram_id INTEGER,
        disponibilite TEXT DEFAULT 'disponible',
        horaires TEXT DEFAULT ''
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categorie TEXT,
        question TEXT,
        reponse TEXT,
        mots_cles TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        probleme TEXT,
        statut TEXT DEFAULT 'ouvert',
        date_creation TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS signalements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        date_creation TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS urgences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        niveau TEXT,
        date_creation TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS annonces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        date_creation TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS disponibilites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre_id INTEGER,
        etat TEXT,
        horaires TEXT,
        date_modification TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS etudiants (
        telegram_id INTEGER PRIMARY KEY,
        nom TEXT,
        etape INTEGER DEFAULT 1,
        date_arrivee TEXT,
        date_modification TEXT
    )
    """)

    conn.commit()
    conn.close()
    
    init_membres()


def init_membres():
    membres = [
        ("Keita Dade", "Président", "+79912697921", ""),
        ("Sacko Lassine", "Vice-président", "+79912435421", "@Lassine223"),
        ("Dembelé Modibo", "Administration", "+79918834425", ""),
        ("Sangaré Ousmane", "Adjoint Administration", "+79161270804", ""),
        ("Traoré Astan B", "Organisation", "+79164452921", ""),
        ("Doumbia Awa", "Adjointe Organisation", "+79303376326", ""),
        ("Doumbia Coumba A", "Communication", "+79569695061", ""),
        ("Keita Fanta S", "Adjointe Communication", "+79851981117", ""),
        ("Thiero Hadja M", "Finance", "+79205714407", ""),
        ("Djiguiba Ousmane", "Adjoint Finance", "+79919204029", ""),
        ("Diarra Moussa K", "Culture", "+79997120179", ""),
        ("Touré Mohamed A", "Adjoint Culture", "+79015976094", ""),
        ("Fané Abdoulaye", "Éducation", "+79773724269", ""),
        ("Sidibé Habou", "Adjoint Éducation", "+79694763734", ""),
        ("Sangaré Issiaka", "Sport", "+79999668502", ""),
        ("Togola Boubacar A", "Adjoint Sport", "+79996747933", ""),
    ]
    for nom, poste, telephone, username in membres:
        execute(
            "INSERT OR IGNORE INTO membres (nom, poste, telephone, username) VALUES (?, ?, ?, ?)",
            (nom, poste, telephone, username),
        )


def execute(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()


def fetchone(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    result = cur.fetchone()
    conn.close()
    return result


def fetchall(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    result = cur.fetchall()
    conn.close()
    return result
