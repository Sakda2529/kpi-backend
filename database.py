# database.py
import sqlite3

DB_FILE = "kpi.db"

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # ป้องกัน lock บน Railway
    return conn