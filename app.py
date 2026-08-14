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
if "tactical_setup" not in st.session_state:
    st.session_state.tactical_setup = {}

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
        new_user = st.text_input("Nom d'utilisateur", key="reg_u")
        new_pass = st.text_input("Mot de passe", type="password", key="reg_p")
        if st.button("S'inscrire"):
            if new_user and new_pass:
                if register_user(new_user, new_pass):
                    st.success("Compte créé !")
                else:
                    st.error("Ce nom existe déjà.")

# --- APPLICATION PRINCIPALE ---
else:
    state = st.session_state.game_state
    
    with st.sidebar:
        st.write(f"👤 **Manager :** {st.session_state.username}")
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
        "📋 Tactique & Composition", 
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
        st.subheader("📋 Gestion de la Tactique et des Postes")
        st.write("Choisissez votre schéma tactique de référence et attribuez vos joueurs à chaque poste sur le terrain.")
        
        # Définition des schémas tactiques et de leurs postes requis
        tactical_formations = {
            "4-3-3 (Équilibré / Offensif)": [
                "Gardien (GK)", 
                "Défenseur Droit (RB)", "Défenseur Central 1 (CB)", "Défenseur Central 2 (CB)", "Défenseur Gauche (LB)",
                "Milieu Défensif (CDM)", "Milieu Relayeur 1 (CM)", "Milieu Relayeur 2 (CM)",
                "Ailier Droit (RW)", "Buteur (ST)", "Ailier Gauche (LW)"
            ],
            "4-4-2 (Classique à plat)": [
                "Gardien (GK)",
                "Défenseur Droit (RB)", "Défenseur Central 1 (CB)", "Défenseur Central 2 (CB)", "Défenseur Gauche (LB)",
                "Milieu Droit (RM)", "Milieu Central 1 (CM)", "Milieu Central 2 (CM)", "Milieu Gauche (LM)",
                "Attaquant 1 (ST)", "Attaquant 2 (ST)"
            ],
            "3-5-2 (Dense dans l'axe)": [
                "Gardien (GK)",
                "Défenseur Central Droit (CB)", "Défenseur Central Axe (CB)", "Défenseur Central Gauche (CB)",
                "Piston Droit (RWB)", "Milieu Central 1 (CM)", "Milieu Meneur (CAM)", "Milieu Central 2 (CM)", "Piston Gauche (LWB)",
                "Attaquant 1 (ST)", "Attaquant 2 (ST)"
            ]
        }
        
        chosen_formation = st.selectbox("Choisir la formation tactique", list(tactical_formations.keys()))
        required_positions = tactical_formations[chosen_formation]
        
        st.markdown("---")
        st.markdown(f"### Visualisation du Onze Type ({chosen_formation})")
        
        # Charger la liste des joueurs disponibles (depuis les fichiers Excel de la base)
        df_players = pd.read_excel(PLAYERS_FILE)
        player_names = df_players["name"].tolist()
        
        # Interface d'affectation poste par poste
        cols_layout = st.columns(2)
        assigned_team = {}
        
        for idx, pos in enumerate(required_positions):
            col_target = cols_layout[idx % 2]
            with col_target:
                selected_player = st.selectbox(f"**{pos}**", ["-- Non assigné --"] + player_names, key=f"pos_{idx}")
                if selected_player != "-- Non assigné --":
                    assigned_team[pos] = selected_player
                    
        st.markdown("---")
        if st.button("Valider et Enregistrer la Composition"):
            st.success(f"La composition en {chosen_formation} a bien été enregistrée pour {state['team_name']} !")
            st.write("Joueurs titulaires positionnés :", assigned_team)

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
                    save_game_state(st.session_state.username, state)
                    st.success(f"Recruté : {player['nom']} !")
                    st.rerun()
                else:
                    st.error("Budget insuffisant.")
                    
    with tab_classement:
        st.subheader("Classement & Stats")
        st.write(f"- **Équipe :** {state['team_name']}")
        st.write(f"- **Matchs joués :** {state['played']}")
        st.write(f"- **Points :** {state['points']}")

    with tab_explorateur:
        st.subheader("Explorateur Excel")
        df_leagues = pd.read_excel(LEAGUES_FILE)
        df_teams = pd.read_excel(TEAMS_FILE)
        df_players_exp = pd.read_excel(PLAYERS_FILE)
        
        ligue_choisie = st.selectbox("Ligue", df_leagues['name'].tolist())
        if ligue_choisie:
            ligue_id = df_leagues[df_leagues['name'] == ligue_choisie]['id'].values[0]
            equipes_filt = df_teams[df_teams['league_id'] == ligue_id]
            equipe_choisie = st.selectbox("Équipe", equipes_filt['name'].tolist())
            if equipe_choisie:
                equipe_id = equipes_filt[equipes_filt['name'] == equipe_choisie]['id'].values[0]
                joueurs_filt = df_players_exp[df_players_exp['team_id'] == equipe_id][['name', 'position', 'rating']]
                st.dataframe(joueurs_filt, use_container_width=True)