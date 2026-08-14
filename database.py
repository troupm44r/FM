import sqlite3
import hashlib
import os

DB_NAME = "football_manager.db"

def init_db():
    # Vérifie si la base existe, sinon elle est créée dans le dossier du projet
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table des utilisateurs
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    
    # Table des sauvegardes de parties
    c.execute('''
        CREATE TABLE IF NOT EXISTS saves (
            username TEXT PRIMARY KEY,
            team_name TEXT,
            budget INTEGER,
            points INTEGER,
            played INTEGER,
            goal_difference INTEGER,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  (username, hash_password(password)))
        c.execute("INSERT INTO saves (username, team_name, budget, points, played, goal_difference) VALUES (?, ?, ?, ?, ?, ?)",
                  (username, f"FC {username}", 50000000, 0, 0, 0))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True
    return False

def load_game_state(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT team_name, budget, points, played, goal_difference FROM saves WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "team_name": row[0],
            "budget": row[1],
            "points": row[2],
            "played": row[3],
            "goal_difference": row[4]
        }
    return None

def save_game_state(username, state):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE saves 
        SET team_name = ?, budget = ?, points = ?, played = ?, goal_difference = ?
        WHERE username = ?
    ''', (state["team_name"], state["budget"], state["points"], state["played"], state["goal_difference"], username))
    conn.commit()
    conn.close()