import sqlite3
from datetime import datetime

DB_PATH = "data/history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_lang TEXT,
            dst_lang TEXT,
            text_input TEXT,
            text_output TEXT,
            context TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_history(src_lang, dst_lang, text_input, text_output, context):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO history (src_lang, dst_lang, text_input, text_output, context, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (src_lang, dst_lang, text_input, text_output, context, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()

def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT src_lang, dst_lang, text_input, text_output, context, created_at FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
