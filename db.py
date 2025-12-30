import os
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL")
DB_PATH = os.getenv("DB_PATH", "events.db")

def get_conn():
    # Local SQLite (no DATABASE_URL)
    if not DATABASE_URL:
        return sqlite3.connect(DB_PATH)

    # Render / Postgres (future-proof)
    import psycopg2
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    if DATABASE_URL:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                description TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL,
                longitude REAL,
                description TEXT,
                category TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

    conn.commit()
    conn.close()


def save_event(user_id: int, lat: float, lng: float, description: str, category: str):
    """Insert a new event into the database."""
    conn = get_conn()
    cursor = conn.cursor()

    if DATABASE_URL:
        cursor.execute(
            "INSERT INTO events (latitude, longitude, description, category) VALUES (%s, %s, %s, %s)",
            (lat, lng, description, category),
        )
    else:
        cursor.execute(
            "INSERT INTO events (latitude, longitude, description, category, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (lat, lng, description, category),
        )

    conn.commit()
    conn.close()


def get_all_events():
    """Return all events as a list of tuples: (latitude, longitude, description, category, created_at)"""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT latitude, longitude, description, category, created_at FROM events ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_events_page(limit: int, offset: int):
    conn = get_conn()
    cursor = conn.cursor()

    if DATABASE_URL:
        cursor.execute(
            "SELECT latitude, longitude, description, category, created_at FROM events ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset),
        )
    else:
        cursor.execute(
            "SELECT latitude, longitude, description, category, created_at FROM events ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_events_count():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]
    conn.close()
    return int(count)
