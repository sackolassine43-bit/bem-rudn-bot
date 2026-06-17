import sqlite3
from config import DATABASE_NAME


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS utilisateurs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        nom TEXT,
        username TEXT,
        date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historique(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        nom TEXT,
        message TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS membres(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        poste TEXT,
        telephone TEXT,
        telegram TEXT,
        disponibilite TEXT DEFAULT 'disponible'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categorie TEXT,
        question TEXT,
        reponse TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alertes_urgence(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        username TEXT,
        message TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
