from flask import Flask, render_template, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Database path (works locally + on Render)
DB_PATH = os.getenv("DB_PATH", "events.db")
print("DB PATH:", DB_PATH)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/events")
def events():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT latitude, longitude, description, category
        FROM events
    """)

    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "lat": row["latitude"],
            "lng": row["longitude"],
            "description": row["description"],
            "category": row["category"]
        } for row in rows
    ])

if __name__ == "__main__":
    app.run(debug=True)
