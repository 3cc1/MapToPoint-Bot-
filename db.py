import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg2.connect(DATABASE_URL)

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION,
                    description TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()

def save_event(user_id, lat, lng, description, category):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (user_id, latitude, longitude, description, category)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, lat, lng, description, category))
        conn.commit()

def get_all_events():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT latitude, longitude, description, category, created_at
                FROM events
                ORDER BY created_at DESC
            """)
            return cur.fetchall()

def get_events_count():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM events")
            return cur.fetchone()[0]

def get_events_page(limit, offset):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT latitude, longitude, description, category, created_at
                FROM events
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            return cur.fetchall()
