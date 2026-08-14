import sqlite3
import hashlib
import os

DB_NAME = "football_manager.db"

def init_db():
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
    
    # Tables du jeu (Ligues, Équipes, Joueurs)
    c.execute('''
        CREATE TABLE IF NOT EXISTS leagues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            league_id INTEGER,
            FOREIGN KEY(league_id) REFERENCES leagues(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            team_id INTEGER,
            position TEXT,
            rating INTEGER,
            FOREIGN KEY(team_id) REFERENCES teams(id)
        )
    ''')
    
    conn.commit()
    
    # Remplir des données par défaut si la base est vide (Ligues majeures et exemples d'équipes/joueurs)
    c.execute("SELECT COUNT(*) FROM leagues")
    if c.fetchone()[0] == 0:
        ligues = ["Ligue 1", "Premier League", "Liga", "Serie A", "Bundesliga"]
        for ligue in ligues:
            c.execute("INSERT INTO leagues (name) VALUES (?)", (ligue,))
        
        conn.commit()
        
        # Données de test / exemples pour alimenter les ligues
        donnees_initiales = [
            ("Ligue 1", "Paris Saint-Germain", [("Kylian Mbappé-like", "Attaquant", 91), ("Ousmane Dembélé", "Attaquant", 84), ("Marquinhos", "Défenseur", 85)]),
            ("Ligue 1", "Olympique de Marseille", [("Pierre-Emerick Aubameyang", "Attaquant", 82), ("Valentin Rongier", "Milieu", 79), ("Chancel Mbemba", "Défenseur", 81)]),
            ("Premier League", "Manchester City", [("Erling Haaland", "Attaquant", 91), ("Kevin De Bruyne", "Milieu", 91), ("Rodri", "Milieu", 89)]),
            ("Premier League", "Arsenal", [("Bukayo Saka", "Attaquant", 86), ("Martin Ødegaard", "Milieu", 87), ("William Saliba", "Défenseur", 85)]),
            ("Liga", "Real Madrid", [("Jude Bellingham", "Milieu", 89), ("Vinicius Jr", "Attaquant", 89), ("Thibaut Courtois", "Gardien", 90)]),
            ("Liga", "FC Barcelone", [("Robert Lewandowski", "Attaquant", 88), ("Pedri", "Milieu", 86), ("Frenkie de Jong", "Milieu", 87)]),
            ("Serie A", "Inter Milan", [("Lautaro Martínez", "Attaquant", 88), ("Nicolò Barella", "Milieu", 86), ("Benjamin Pavard", "Défenseur", 84)]),
            ("Serie A", "AC Milan", [("Rafael Leão", "Attaquant", 86), ("Theo Hernández", "Défenseur", 85), ("Mike Maignan", "Gardien", 87)]),
            ("Bundesliga", "Bayern Munich", [("Harry Kane", "Attaquant", 90), ("Jamal Musiala", "Milieu", 86), ("Manuel Neuer", "Gardien", 87)]),
            ("Bundesliga", "Bayer Leverkusen", [("Florian Wirtz", "Milieu", 85), ("Victor Boniface", "Attaquant", 82), ("Granit Xhaka", "Milieu", 83)])
        ]
        
        for ligue_nom, equipe_nom, joueurs in donnees_initiales:
            c.execute("SELECT id FROM leagues WHERE name = ?", (ligue_nom,))
            l_id = c.fetchone()[0]
            c.execute("INSERT INTO teams (name, league_id) VALUES (?, ?)", (equipe_nom, l_id))
            t_id = c.lastrowid
            for p_nom, p_pos, p_note in joueurs:
                c.execute("INSERT INTO players (name, team_id, position, rating) VALUES (?, ?, ?, ?)", (p_nom, t_id, p_pos, p_note))
                
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