import sys
import os
# Add project root to path so `from db import ...` works when running this file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from db import init_db
import sqlite3


app = Flask(__name__)
CORS(app)

DB_PATH = os.getenv("DB_PATH", "events.db")

# ✅ CREATE TABLE IF MISSING
init_db()
