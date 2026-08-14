import os
import pandas as pd
import hashlib

DATA_DIR = "data"

USERS_FILE = os.path.join(DATA_DIR, "users.xlsx")
SAVES_FILE = os.path.join(DATA_DIR, "saves.xlsx")
LEAGUES_FILE = os.path.join(DATA_DIR, "leagues.xlsx")
TEAMS_FILE = os.path.join(DATA_DIR, "teams.xlsx")
PLAYERS_FILE = os.path.join(DATA_DIR, "players.xlsx")

def init_db():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    if not os.path.exists(USERS_FILE):
        df_users = pd.DataFrame(columns=["username", "password"])
        df_users.to_excel(USERS_FILE, index=False)
        
    # Ajout de la colonne selected_team pour stocker le club choisi à l'inscription
    if not os.path.exists(SAVES_FILE):
        df_saves = pd.DataFrame(columns=["username", "team_name", "selected_team", "budget", "points", "played", "goal_difference"])
        df_saves.to_excel(SAVES_FILE, index=False)
        
    if not os.path.exists(LEAGUES_FILE):
        df_leagues = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Ligue 1", "Premier League", "Liga", "Serie A", "Bundesliga"]
        })
        df_leagues.to_excel(LEAGUES_FILE, index=False)
        
    if not os.path.exists(TEAMS_FILE):
        # Liste complète des clubs pour les 5 championnats
        teams_data = [
            # Ligue 1 (id: 1)
            (1, "Paris Saint-Germain", 1), (2, "Olympique de Marseille", 1), (3, "AS Monaco", 1), 
            (4, "LOSC Lille", 1), (5, "Olympique Lyonnais", 1), (6, "Stade Rennais FC", 1),
            # Premier League (id: 2)
            (7, "Manchester City", 2), (8, "Arsenal FC", 2), (9, "Liverpool FC", 2), 
            (10, "Manchester United", 2), (11, "Chelsea FC", 2), (12, "Tottenham Hotspur", 2),
            # Liga (id: 3)
            (13, "Real Madrid", 3), (14, "FC Barcelona", 3), (15, "Atletico Madrid", 3), 
            (16, "Real Sociedad", 3), (17, "Villarreal CF", 3), (18, "Real Betis", 3),
            # Serie A (id: 4)
            (19, "Inter Milan", 4), (20, "AC Milan", 4), (21, "Juventus Turin", 4), 
            (22, "Napoli", 4), (23, "AS Roma", 4), (24, "Atalanta", 4),
            # Bundesliga (id: 5)
            (25, "Bayern Munich", 5), (26, "Borussia Dortmund", 5), (27, "Bayer Leverkusen", 5), 
            (28, "RB Leipzig", 5), (29, "Eintracht Frankfurt", 5), (30, "VfB Stuttgart", 5)
        ]
        df_teams = pd.DataFrame(teams_data, columns=["id", "name", "league_id"])
        df_teams.to_excel(TEAMS_FILE, index=False)
        
    if not os.path.exists(PLAYERS_FILE):
        # Génération automatique d'un effectif de 20 joueurs (11 titulaires + 9 remplaçants) pour chaque club (30 clubs * 20 = 600 joueurs)
        players_data = []
        player_id = 1
        postes_titulaires = ["Gardien", "Défenseur", "Défenseur", "Défenseur", "Défenseur", "Milieu", "Milieu", "Milieu", "Attaquant", "Attaquant", "Attaquant"]
        postes_remplacants = ["Gardien R.", "Défenseur R.", "Défenseur R.", "Milieu R.", "Milieu R.", "Milieu R.", "Attaquant R.", "Attaquant R.", "Attaquant R."]
        
        df_t = pd.read_excel(TEAMS_FILE)
        for _, team in df_t.iterrows():
            t_id = team["id"]
            t_name = team["name"]
            
            # 11 titulaires
            for i, p in enumerate(postes_titulaires):
                players_data.append((player_id, f"Joueur {p[0]}-{i+1} ({t_name[:3]})", t_id, p, 80 + (i % 10)))
                player_id += 1
            # 9 remplaçants
            for i, p in enumerate(postes_remplacants):
                players_data.append((player_id, f"Remplaçant-{i+1} ({t_name[:3]})", t_id, p, 73 + (i % 7)))
                player_id += 1
                
        df_players = pd.DataFrame(players_data, columns=["id", "name", "team_id", "position", "rating"])
        df_players.to_excel(PLAYERS_FILE, index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, selected_team):
    df_users = pd.read_excel(USERS_FILE)
    if username in df_users["username"].values:
        return False
    
    new_user = pd.DataFrame([[username, hash_password(password)]], columns=["username", "password"])
    df_users = pd.concat([df_users, new_user], ignore_index=True)
    df_users.to_excel(USERS_FILE, index=False)
    
    df_saves = pd.read_excel(SAVES_FILE)
    new_save = pd.DataFrame([[username, selected_team, selected_team, 50000000, 0, 0, 0]], 
                            columns=["username", "team_name", "selected_team", "budget", "points", "played", "goal_difference"])
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
            "selected_team": save_row.iloc[0]["selected_team"],
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