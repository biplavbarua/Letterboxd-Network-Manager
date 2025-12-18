import sqlite3
import datetime
import logging

DB_NAME = "network_manager.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table: follow_history
    # Tracks who we followed and when
    c.execute('''
        CREATE TABLE IF NOT EXISTS follow_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'followed'
        )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("Database initialized.")

def log_follow(username):
    """Log a successful follow action."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO follow_history (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()

def get_today_follow_count():
    """Get number of follows performed today."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # SQLite 'start of day' logic
    c.execute("SELECT COUNT(*) FROM follow_history WHERE date(followed_at) = date('now')")
    count = c.fetchone()[0]
    conn.close()
    return count

def is_already_followed(username):
    """Check if we have already followed this user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM follow_history WHERE username = ?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists
