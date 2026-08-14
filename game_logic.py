import random

def simulate_match(user_team_name):
    opponent_names = ["Olympique de Streamlit", "Python Athletic", "SQL City", "Pandas United", "Flask FC"]
    opponent = random.choice(opponent_names)
    
    user_goals = random.randint(0, 4)
    opp_goals = random.randint(0, 4)
    
    if user_goals > opp_goals:
        result = "Victoire"
        points_earned = 3
    elif user_goals == opp_goals:
        result = "Match nul"
        points_earned = 1
    else:
        result = "Défaite"
        points_earned = 0
        
    gd_earned = user_goals - opp_goals
    
    match_summary = f"Match contre **{opponent}** : **{user_goals} - {opp_goals}** ({result})"
    return match_summary, points_earned, gd_earned

def get_transfer_market():
    return [
        {"nom": "Super Buteur", "poste": "Attaquant", "prix": 25000000, "note": 88},
        {"nom": "Maestro du Milieu", "poste": "Milieu", "prix": 20000000, "note": 86},
        {"nom": "Mur Défensif", "poste": "Défenseur", "prix": 15000000, "note": 85},
        {"nom": "Gardien de Coffre", "poste": "Gardien", "prix": 12000000, "note": 83},
    ]