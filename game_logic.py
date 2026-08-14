import streamlit as st
import pandas as pd
import sqlite3
from database import init_db, register_user, verify_user, load_game_state, save_game_state, DB_NAME
from game_logic import simulate_match, get_transfer_market

# Initialisation de la base de données
init_db()

st.set_page_config(page_title="Mini Football Manager", page_icon="⚽", layout="wide")

# Gestion de la session utilisateur
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "game_state" not in st.session_state:
    st.session_state.game_state = None

# --- ÉCRAN DE CONNEXION / INSCRIPTION ---
if not st.session_state.logged_in:
    st.title("⚽ Bienvenue dans Mini Football Manager")
    st.markdown("Connectez-vous ou créez un compte pour lancer votre carrière d'entraîneur !")
    
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    
    with tab1:
        st.subheader("Se connecter")
        login_user = st.text_input("Nom d'utilisateur", key="login_u")
        login_pass = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("Connexion"):
            if verify_user(login_user, login_pass):
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.session_state.game_state = load_game_state(login_user)
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")
                
    with tab2:
        st.subheader("Créer un compte")
        new_user = st.text_input("Choisissez un nom d'utilisateur", key="reg_u")
        new_pass = st.text_input("Choisissez un mot de passe", type="password", key="reg_p")
        if st.button("S'inscrire"):
            if new_user and new_pass:
                if register_user(new_user, new_pass):
                    st.success("Compte créé avec succès ! Vous pouvez vous connecter.")
                else:
                    st.error("Ce nom d'utilisateur existe déjà.")
            else:
                st.warning("Veuillez remplir tous les champs.")

# --- APPLICATION PRINCIPALE (SI CONNECTÉ) ---
else:
    state = st.session_state.game_state
    
    # Barre latérale (Sidebar) - Infos manager & Déconnexion
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
        st.metric(label="Points au classement", value=state["points"])
        
        st.markdown("---")
        if st.button("💾 Sauvegarder la partie"):
            save_game_state(st.session_state.username, state)
            st.success("Partie sauvegardée !")
            
        st.markdown("---")
        
        # Panneau Administrateur
        with st.expander("🛠️ Mode Administrateur"):
            admin_pass = st.text_input("Mot de passe admin", type="password", key="admin_pwd")
            if admin_pass == "mon_super_secret_admin":
                st.success("Accès admin autorisé")
                conn = sqlite3.connect(DB_NAME)
                df_users = pd.read_sql("SELECT * FROM users", conn)
                df_saves = pd.read_sql("SELECT * FROM saves", conn)
                conn.close()
                
                st.write("**Table Users**")
                st.dataframe(df_users)
                st.write("**Table Saves**")
                st.dataframe(df_saves)
            elif admin_pass:
                st.error("Mot de passe incorrect")

        st.markdown("---")
        if st.button("Déconnexion"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.game_state = None
            st.rerun()

    # Contenu principal - Onglets du jeu
    st.title(f"🏟️ Tableau de Bord - {state['team_name']}")
    
    tab_match, tab_transferts, tab_classement, tab_explorateur = st.tabs([
        "📅 Jouer un Match", 
        "🛒 Marché des Transferts", 
        "🏆 Classement & Stats", 
        "🌍 Explorateur d'Équipes"
    ])
    
    with tab_match:
        st.subheader("Prochaine journée de championnat")
        st.write("Préparez votre équipe et lancez le match du week-end !")
        
        if st.button("▶️ Jouer le match", type="primary"):
            summary, pts, gd = simulate_match(state["team_name"])
            state["played"] += 1
            state["points"] += pts
            state["goal_difference"] += gd
            save_game_state(st.session_state.username, state)
            
            st.markdown(f"### Résultat :")
            st.info(summary)
            st.rerun()
            
    with tab_transferts:
        st.subheader("Acheter des joueurs")
        st.write("Renforcez votre effectif pour grimper au classement.")
        
        market = get_transfer_market()
        for i, player in enumerate(market):
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(f"**{player['nom']}** ({player['poste']}) - Note : {player['note']}")
            col2.write(f"Prix : {player['prix']:,} €")
            if col3.button(f"Acheter", key=f"buy_{i}"):
                if state["budget"] >= player["prix"]:
                    state["budget"] -= player["prix"]
                    save_game_state(st.session_state.username, state)
                    st.success(f"Vous avez recruté {player['nom']} !")
                    st.rerun()
                else:
                    st.error("Budget insuffisant !")
                    
    with tab_classement:
        st.subheader("Statistiques de l'équipe")
        st.write(f"- **Équipe :** {state['team_name']}")
        st.write(f"- **Matchs joués :** {state['played']}")
        st.write(f"- **Points :** {state['points']}")
        st.write(f"- **Différence de buts :** {state['goal_difference']}")

    with tab_explorateur:
        st.subheader("🌍 Explorer les championnats et effectifs mondiaux")
        st.write("Visualisez n'importe quelle équipe de Ligue 1, Premier League, Liga, Serie A ou Bundesliga.")
        
        conn = sqlite3.connect(DB_NAME)
        ligues_df = pd.read_sql("SELECT name FROM leagues", conn)
        ligue_choisie = st.selectbox("Choisir une ligue", ligues_df['name'].tolist(), key="select_league")
        
        if ligue_choisie:
            equipes_df = pd.read_sql(f"""
                SELECT t.name 
                FROM teams t 
                JOIN leagues l ON t.league_id = l.id 
                WHERE l.name = '{ligue_choisie}'
            """, conn)
            
            equipe_choisie = st.selectbox("Choisir une équipe", equipes_df['name'].tolist(), key="select_team")
            
            if equipe_choisie:
                joueurs_df = pd.read_sql(f"""
                    SELECT p.name AS "Joueur", p.position AS "Poste", p.rating AS "Note"
                    FROM players p 
                    JOIN teams t ON p.team_id = t.id 
                    WHERE t.name = '{equipe_choisie}'
                """, conn)
                
                st.markdown(f"### Effectif de {equipe_choisie}")
                st.dataframe(joueurs_df, use_container_width=True)
                
        conn.close()