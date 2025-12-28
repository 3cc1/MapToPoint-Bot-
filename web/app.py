from flask import Flask, render_template, jsonify 
import sqlite3
import os 

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'C:\MapToPoint\events.db')
print("DB PATH:", DB_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT latitude, longitude, description, category
        FROM events
    """)

    rows = cursor.fetchall()
    conn.close()        

    return jsonify([
        {
            "lat": r[0],
            "lng": r[1],
            "description": r[2],
            "category": r[3]
        } for r in rows
    ])
if __name__ == '__main__':
    app.run(debug=True)

