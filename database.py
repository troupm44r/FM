import os
import pandas as pd
import hashlib

DATA_DIR = "data"

# Noms des fichiers Excel par table
USERS_FILE = os.path.join(DATA_DIR, "users.xlsx")
SAVES_FILE = os.path.join(DATA_DIR, "saves.xlsx")
LEAGUES_FILE = os.path.join(DATA_DIR, "leagues.xlsx")
TEAMS_FILE = os.path.join(DATA_DIR, "teams.xlsx")
PLAYERS_FILE = os.path.join(DATA_DIR, "players.xlsx")

def init_db():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    # 1. users.xlsx
    if not os.path.exists(USERS_FILE):
        df_users = pd.DataFrame(columns=["username", "password"])
        df_users.to_excel(USERS_FILE, index=False)
        
    # 2. saves.xlsx
    if not os.path.exists(SAVES_FILE):
        df_saves = pd.DataFrame(columns=["username", "team_name", "budget", "points", "played", "goal_difference"])
        df_saves.to_excel(SAVES_FILE, index=False)
        
    # 3. leagues.xlsx
    if not os.path.exists(LEAGUES_FILE):
        df_leagues = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Ligue 1", "Premier League", "Liga", "Serie A", "Bundesliga"]
        })
        df_leagues.to_excel(LEAGUES_FILE, index=False)
        
    # 4. teams.xlsx
    if not os.path.exists(TEAMS_FILE):
        df_teams = pd.DataFrame({
            "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "name": [
                "Paris Saint-Germain", "Olympique de Marseille", 
                "Manchester City", "Arsenal", 
                "Real Madrid", "FC Barcelone", 
                "Inter Milan", "AC Milan", 
                "Bayern Munich", "Bayer Leverkusen"
            ],
            "league_id": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        })
        df_teams.to_excel(TEAMS_FILE, index=False)
        
    # 5. players.xlsx
    if not os.path.exists(PLAYERS_FILE):
        df_players = pd.DataFrame({
            "id": list(range(1, 31)),
            "name": [
                "Kylian Mbappé-like", "Ousmane Dembélé", "Marquinhos",
                "Pierre-Emerick Aubameyang", "Valentin Rongier", "Chancel Mbemba",
                "Erling Haaland", "Kevin De Bruyne", "Rodri",
                "Bukayo Saka", "Martin Ødegaard", "William Saliba",
                "Jude Bellingham", "Vinicius Jr", "Thibaut Courtois",
                "Robert Lewandowski", "Pedri", "Frenkie de Jong",
                "Lautaro Martínez", "Nicolò Barella", "Benjamin Pavard",
                "Rafael Leão", "Theo Hernández", "Mike Maignan",
                "Harry Kane", "Jamal Musiala", "Manuel Neuer",
                "Florian Wirtz", "Victor Boniface", "Granit Xhaka"
            ],
            "team_id": [
                1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 
                6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10
            ],
            "position": [
                "Attaquant", "Attaquant", "Défenseur", "Attaquant", "Milieu", "Défenseur",
                "Attaquant", "Milieu", "Milieu", "Attaquant", "Milieu", "Défenseur",
                "Milieu", "Attaquant", "Gardien", "Attaquant", "Milieu", "Milieu",
                "Attaquant", "Milieu", "Défenseur", "Attaquant", "Défenseur", "Gardien",
                "Attaquant", "Milieu", "Gardien", "Milieu", "Attaquant", "Milieu"
            ],
            "rating": [
                91, 84, 85, 82, 79, 81, 91, 91, 89, 86, 87, 85, 
                89, 89, 90, 88, 86, 87, 88, 86, 84, 86, 85, 87, 
                90, 86, 87, 85, 82, 83
            ]
        })
        df_players.to_excel(PLAYERS_FILE, index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    df_users = pd.read_excel(USERS_FILE)
    if username in df_users["username"].values:
        return False
    
    # Ajouter l'utilisateur
    new_user = pd.DataFrame([[username, hash_password(password)]], columns=["username", "password"])
    df_users = pd.concat([df_users, new_user], ignore_index=True)
    df_users.to_excel(USERS_FILE, index=False)
    
    # Créer sa sauvegarde initiale
    df_saves = pd.read_excel(SAVES_FILE)
    new_save = pd.DataFrame([[username, f"FC {username}", 50000000, 0, 0, 0]], 
                            columns=["username", "team_name", "budget", "points", "played", "goal_difference"])
    df_saves = pd.concat([df_saves, new_save], ignore_index=True)
    df_saves.to_excel(SAVES_FILE, index=False)
    
    return True

def verify_user(username, password):
    df_users = pd.read_excel(USERS_FILE)
    user_row = df_users[df_users["username"] == username]
    if not user_row.empty:
        if user_row.iloc[0]["password"] == hash_password(password):
            return True
    return False

def load_game_state(username):
    df_saves = pd.read_excel(SAVES_FILE)
    save_row = df_saves[df_saves["username"] == username]
    if not save_row.empty:
        return {
            "team_name": save_row.iloc[0]["team_name"],
            "budget": int(save_row.iloc[0]["budget"]),
            "points": int(save_row.iloc[0]["points"]),
            "played": int(save_row.iloc[0]["played"]),
            "goal_difference": int(save_row.iloc[0]["goal_difference"])
        }
    return None

def save_game_state(username, state):
    df_saves = pd.read_excel(SAVES_FILE)
    df_saves.loc[df_saves["username"] == username, ["team_name", "budget", "points", "played", "goal_difference"]] = [
        state["team_name"], state["budget"], state["points"], state["played"], state["goal_difference"]
    ]
    df_saves.to_excel(SAVES_FILE, index=False)