from flask import Flask, render_template, jsonify
from flask_cors import CORS
from db import init_db, get_all_events

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/events")
def events():
    rows = get_all_events()
    return jsonify([
        {
            "lat": r[0],
            "lng": r[1],
            "description": r[2],
            "category": r[3]
        } for r in rows
    ])

if __name__ == "__main__":
    init_db()
    app.run()
