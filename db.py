import sqlite3
from datetime import datetime
DB_NAME = "events.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        conn.execute("""        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            latitude REAL,
            longitude REAL,
            description TEXT,
            category TEXT,
            created_at TEXT
        )
        """)

def save_event(user_id, lat, lng, description, category):
    with get_connection() as conn:
        conn.execute("""
                             INSERT INTO events (user_id, latitude, longitude, description, category, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, lat, lng, description, category, datetime.utcnow()))

def get_all_events():
    with get_connection() as conn:
        cursor = conn.execute("""            
            SELECT latitude, longitude, description, category, created_at
            FROM events
        """)
        return cursor.fetchall()
    
def get_events_page(limit = 15, offset = 0):
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT latitude, longitude, description, category, created_at
            FROM events
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        return cursor.fetchall()
    
def get_events_count():
    with get_connection() as conn:
        with get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM events")
            return cursor.fetchone()[0]
        
