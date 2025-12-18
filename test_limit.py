
import sqlite3
import requests
import json
import database

DB_NAME = "network_manager.db"

def mock_fill_db():
    print("Mocking 50 follows in DB...")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for i in range(50):
        username = f"mock_user_{i}"
        c.execute("INSERT INTO follow_history (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()
    print("DB filled with 50 follows.")

def test_limit_reached():
    print("Testing /api/follow with limit reached...")
    url = "http://127.0.0.1:5000/api/follow"
    payload = {
        "username": "victim_user",
        "cookies": "mock_cookie=123"
    }
    try:
        res = requests.post(url, json=payload)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        if res.status_code == 400 and "Daily limit reached" in res.json().get('message', ''):
            print("PASS: Daily limit correctly enforced.")
        else:
            print("FAIL: Daily limit NOT enforced.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    mock_fill_db()
    test_limit_reached()
