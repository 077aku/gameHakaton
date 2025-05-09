# src/database.py
import sqlite3

conn = None

def init_db():
    global conn
    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            score INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

def get_connection():
    global conn
    if conn is None:
        raise RuntimeError("Database not initialized")
    return conn

def update_score(player_id, score):
    cursor = get_connection().cursor()
    cursor.execute("UPDATE players SET score = ? WHERE id = ? AND score < ?", (score, player_id, score))
    conn.commit()

def get_leaderboard(limit=5):
    cursor = get_connection().cursor()
    cursor.execute("SELECT name, score FROM players ORDER BY score DESC LIMIT ?", (limit,))
    return cursor.fetchall()

def close_db():
    global conn
    if conn:
        conn.close()
        conn = None
