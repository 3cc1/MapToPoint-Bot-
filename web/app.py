from flask import Flask, render_template, jsonify
from flask_cors import CORS
from db import init_db
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.getenv("DB_PATH", "events.db")

# ✅ CREATE TABLE IF MISSING
init_db()
