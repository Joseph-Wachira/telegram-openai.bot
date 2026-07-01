import sqlite3
import datetime
from config import DATABASE_PATH
import os

def get_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_seen TIMESTAMP,
            request_count INTEGER DEFAULT 0,
            token_usage INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def update_user(user_id: int, username: str = None, first_name: str = None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, username, first_name, last_seen, request_count)
        VALUES (?, ?, ?, ?, 1)
        ON CONFLICT(user_id) DO UPDATE SET
            username = COALESCE(?, username),
            first_name = COALESCE(?, first_name),
            last_seen = ?,
            request_count = request_count + 1
    ''', (user_id, username, first_name, datetime.datetime.now(),
          username, first_name, datetime.datetime.now()))
    conn.commit()
    conn.close()

def update_token_usage(user_id: int, tokens: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET token_usage = token_usage + ? WHERE user_id = ?
    ''', (tokens, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY last_seen DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_stats(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None