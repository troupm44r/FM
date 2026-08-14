import streamlit as st
import pandas as pd
import os
from database import init_db, register_user, verify_user, load_game_state, save_game_state, USERS_FILE, SAVES_FILE, LEAGUES_FILE, TEAMS_FILE, PLAYERS_FILE
from game_logic import simulate_match, get_transfer_market

init_db()

st.set_page_config(page_title="Mini Football Manager", page_icon="⚽", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "game_state" not in st.session_state:
    st.session_state.game_state = None

# --- CONNEXION / INSCRIPTION ---
if not st.session_state.logged_in:
    st.title("⚽ Bienvenue dans Mini Football Manager")
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    
    with tab1:
        login_user = st.text_input("Nom d'utilisateur", key="login_u")
        login_pass = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("Connexion"):
            if verify_user(login_user, login_pass):
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.session_state.game_state = load_game_state(login_user)
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")
                
    with tab2:
        st.subheader("Créer un compte et choisir son club")
        new_user = st.text_input("Nom d'utilisateur", key="reg_u")
        new_pass = st.text_input("Mot de passe", type="password", key="reg_p")
        
        # Sélection du championnat et du club à l'inscription
        df_leagues = pd.read_excel(LEAGUES_FILE)
        df_teams = pd.read_excel(TEAMS_FILE)
        
        reg_league = st.selectbox("Choisir le championnat de départ", df_leagues['name'].tolist(), key="reg_l")
        league_id = df_leagues[df_leagues['name'] == reg_league]['id'].values[0]
        teams_in_league = df_teams[df_teams['league_id'] == league_id]['name'].tolist()
        
        reg_team = st.selectbox("Choisir votre club", teams_in_league, key="reg_t")
        
        if st.button("S'inscrire avec ce club"):
            if new_user and new_pass:
                if register_user(new_user, new_pass, reg_team):
                    st.success("Compte créé avec succès ! Vous pouvez vous connecter.")
                else:
                    st.error("Ce nom d'utilisateur existe déjà.")
            else:
                st.warning("Veuillez remplir tous les champs.")

# --- APPLICATION PRINCIPALE ---
else:
    state = st.session_state.game_state
    
    with st.sidebar:
        st.write(f"👤 **Manager :** {st.session_state.username}")
        st.write(f"🛡️ **Club :** {state['selected_team']}")
        st.text_input("Nom de l'équipe", value=state["team_name"], key="input_team_name")
        if st.button("Mettre à jour le nom"):
            state["team_name"] = st.session_state.input_team_name
            save_game_state(st.session_state.username, state)
            st.success("Nom sauvegardé !")
            
        st.markdown("---")
        st.metric(label="Budget", value=f"{state['budget']:,} €")
        st.metric(label="Matchs joués", value=state["played"])
        st.metric(label="Points", value=state["points"])
        
        st.markdown("---")
        if st.button("💾 Sauvegarder"):
            save_game_state(st.session_state.username, state)
            st.success("Sauvegardé !")
            
        st.markdown("---")
        if st.button("Déconnexion"):
            st.session_state.logged_in = False
            st.rerun()

    st.title(f"🏟️ Tableau de Bord - {state['team_name']}")
    
    tab_match, tab_tactique, tab_transferts, tab_classement, tab_explorateur = st.tabs([
        "📅 Match", 
        "📋 Tactique & Composition (11 + 9)", 
        "🛒 Transferts", 
        "🏆 Classement", 
        "🌍 Explorateur"
    ])
    
    with tab_match:
        st.subheader("Prochaine journée")
        if st.button("▶️ Jouer le match", type="primary"):
            summary, pts, gd = simulate_match(state["team_name"])
            state["played"] += 1
            state["points"] += pts
            state["goal_difference"] += gd
            save_game_state(st.session_state.username, state)
            st.info(summary)
            st.rerun()
            
    with tab_tactique:
        st.subheader("📋 Gestion de l'effectif (11 Titulaires & 9 Remplaçants)")
        st.write(f"Effectif officiel de votre club : **{state['selected_team']}**")
        
        # Récupérer les joueurs du club choisi par l'utilisateur
        df_teams = pd.read_excel(TEAMS_FILE)
        df_players = pd.read_excel(PLAYERS_FILE)
        
        team_id = df_teams[df_teams['name'] == state['selected_team']]['id'].values[0]
        club_players = df_players[df_players['team_id'] == team_id]
        
        player_names = club_players["name"].tolist()
        
        tactical_formations = {
            "4-3-3": [
                "Gardien (GK)", 
                "Défenseur Droit (RB)", "Défenseur Central 1 (CB)", "Défenseur Central 2 (CB)", "Défenseur Gauche (LB)",
                "Milieu Défensif (CDM)", "Milieu Relayeur 1 (CM)", "Milieu Relayeur 2 (CM)",
                "Ailier Droit (RW)", "Buteur (ST)", "Ailier Gauche (LW)"
            ],
            "4-4-2": [
                "Gardien (GK)",
                "Défenseur Droit (RB)", "Défenseur Central 1 (CB)", "Défenseur Central 2 (CB)", "Défenseur Gauche (LB)",
                "Milieu Droit (RM)", "Milieu Central 1 (CM)", "Milieu Central 2 (CM)", "Milieu Gauche (LM)",
                "Attaquant 1 (ST)", "Attaquant 2 (ST)"
            ],
            "3-5-2": [
                "Gardien (GK)",
                "Défenseur Central Droit (CB)", "Défenseur Central Axe (CB)", "Défenseur Central Gauche (CB)",
                "Piston Droit (RWB)", "Milieu Central 1 (CM)", "Milieu Meneur (CAM)", "Milieu Central 2 (CM)", "Piston Gauche (LWB)",
                "Attaquant 1 (ST)", "Attaquant 2 (ST)"
            ]
        }
        
        chosen_formation = st.selectbox("Choisir la formation tactique (11 Titulaires)", list(tactical_formations.keys()))
        required_positions = tactical_formations[chosen_formation]
        
        st.markdown("### 🟢 Onze Titulaire")
        cols_layout = st.columns(2)
        assigned_starters = []
        for idx, pos in enumerate(required_positions):
            with cols_layout[idx % 2]:
                sel = st.selectbox(f"**{pos}**", ["-- Choisir un joueur --"] + player_names, key=f"start_{idx}")
                if sel != "-- Choisir un joueur --":
                    assigned_starters.append(sel)
                    
        st.markdown("---")
        st.markdown("### 🔵 Banc des Remplaçants (9 Joueurs)")
        sub_cols = st.columns(3)
        assigned_subs = []
        for i in range(9):
            with sub_cols[i % 3]:
                sel_sub = st.selectbox(f"Remplaçant {i+1}", ["-- Choisir un remplaçant --"] + player_names, key=f"sub_{i}")
                if sel_sub != "-- Choisir un joueur --":
                    assigned_subs.append(sel_sub)
                    
        if st.button("Enregistrer la feuille de match"):
            st.success(f"Composition enregistrée avec succès ({len(assigned_starters)} titulaires et {len(assigned_subs)} remplaçants) !")

    with tab_transferts:
        st.subheader("Marché des transferts")
        market = get_transfer_market()
        for i, player in enumerate(market):
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(f"**{player['nom']}** ({player['poste']}) - Note : {player['note']}")
            col2.write(f"Prix : {player['prix']:,} €")
            if col3.button("Acheter", key=f"buy_{i}"):
                if state["budget"] >= player["prix"]:
                    state["budget"] -= player["prix"]
                    save_game_state(state["username"], state)
                    st.success(f"Recruté : {player['nom']} !")
                    st.rerun()
                else:
                    st.error("Budget insuffisant.")
                    
    with tab_classement:
        st.subheader("Classement & Stats")
        st.write(f"- **Club d'origine :** {state['selected_team']}")
        st.write(f"- **Matchs joués :** {state['played']}")
        st.write(f"- **Points :** {state['points']}")

    with tab_explorateur:
        st.subheader("Explorateur Excel global")
        df_l = pd.read_excel(LEAGUES_FILE)
        df_t = pd.read_excel(TEAMS_FILE)
        df_p = pd.read_excel(PLAYERS_FILE)
        
        ligue_c = st.selectbox("Ligue", df_l['name'].tolist(), key="exp_l")
        if ligue_c:
            l_id = df_l[df_l['name'] == ligue_c]['id'].values[0]
            teams_f = df_t[df_t['league_id'] == l_id]
            team_c = st.selectbox("Équipe", teams_f['name'].tolist(), key="exp_t")
            if team_c:
                t_id = teams_f[teams_f['name'] == team_c]['id'].values[0]
                players_f = df_p[df_p['team_id'] == t_id][['name', 'position', 'rating']]
                players_f.columns = ["Nom", "Poste", "Note"]
                st.dataframe(players_f, use_container_width=True)