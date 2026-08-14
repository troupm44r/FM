import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import os
from .utils.database import (
    load_data, save_data, get_equipes, get_joueurs_by_equipe,
    get_championnats, get_classement, update_classement,
    get_calendrier, update_match, get_tactiques,
    get_postes, update_tactique_joueur, get_utilisateur,
    add_utilisateur, get_offres_transfert, add_offre_transfert,
    update_transfert, get_ligue_des_champions, get_matchs_ldc
)
from .utils.simulation import simuler_match
from .utils.transferts import generer_offres_ia, traiter_offre

# --- Configuration de la page ---
st.set_page_config(
    page_title="Football Manager",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Variables globales ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Fonctions utilitaires ---
def init_data():
    """Initialise les données si les fichiers n'existent pas."""
    fichiers = [
        "equipes", "joueurs", "championnats", "calendrier",
        "classements", "tactiques", "postes", "tactique_joueurs",
        "transferts", "utilisateurs", "ligue_des_champions",
        "matchs_ldc", "offres_transfert"
    ]
    for fichier in fichiers:
        path = os.path.join(DATA_DIR, f"{fichier}.xlsx")
        if not os.path.exists(path):
            df = pd.DataFrame()
            if fichier == "equipes":
                df = pd.DataFrame(columns=[
                    "id_equipe", "nom", "pays", "championnat", "budget_transfert",
                    "valeur_marchande", "stade", "capacite_stade", "entraineur",
                    "classement", "points", "buts_pour", "buts_contre",
                    "victoires", "nuls", "defaites"
                ])
            elif fichier == "joueurs":
                df = pd.DataFrame(columns=[
                    "id_joueur", "nom", "prenom", "age", "nationalite", "poste",
                    "poste_secondaire", "pied_fort", "taille", "poids",
                    "valeur_marche", "salaire", "id_equipe", "contrat_jusqu_a",
                    "note_generale", "atq_finition", "atq_passe", "atq_dribbles",
                    "atq_tir", "mil_defensif", "mil_offensif", "mil_passe",
                    "def_defense", "def_tacle", "def_interception", "def_aérien",
                    "gard_arret", "gard_reflexe", "gard_placement", "vitesse",
                    "endurance", "force", "agilite"
                ])
            elif fichier == "championnats":
                df = pd.DataFrame(columns=[
                    "id_championnat", "nom", "pays", "niveau",
                    "nombre_equipes", "saison_actuelle"
                ])
            elif fichier == "calendrier":
                df = pd.DataFrame(columns=[
                    "id_match", "id_championnat", "id_equipe_domicile",
                    "id_equipe_exterieur", "date_match", "heure_match",
                    "journee", "stade", "score_domicile", "score_exterieur",
                    "statut", "simule"
                ])
            elif fichier == "classements":
                df = pd.DataFrame(columns=[
                    "id_classement", "id_championnat", "id_equipe",
                    "position", "points", "victoires", "nuls", "defaites",
                    "buts_pour", "buts_contre", "diff_buts", "matchs_joues"
                ])
            elif fichier == "tactiques":
                df = pd.DataFrame(columns=[
                    "id_tactique", "nom", "description", "formation"
                ])
            elif fichier == "postes":
                df = pd.DataFrame(columns=[
                    "id_poste", "nom", "type", "abreviation"
                ])
            elif fichier == "tactique_joueurs":
                df = pd.DataFrame(columns=[
                    "id", "id_equipe", "id_joueur", "id_poste",
                    "id_tactique", "position_x", "position_y"
                ])
            elif fichier == "transferts":
                df = pd.DataFrame(columns=[
                    "id_transfert", "id_joueur", "id_equipe_ancienne",
                    "id_equipe_nouvelle", "date_transfert", "montant",
                    "type", "duree_pret"
                ])
            elif fichier == "utilisateurs":
                df = pd.DataFrame(columns=[
                    "id_utilisateur", "nom", "email", "mot_de_passe",
                    "id_equipe", "date_inscription", "derniere_connexion"
                ])
            elif fichier == "ligue_des_champions":
                df = pd.DataFrame(columns=[
                    "id", "id_equipe", "id_championnat", "saison",
                    "phase", "groupe", "points"
                ])
            elif fichier == "matchs_ldc":
                df = pd.DataFrame(columns=[
                    "id_match_ldc", "id_equipe_domicile", "id_equipe_exterieur",
                    "date_match", "phase", "groupe", "score_domicile",
                    "score_exterieur", "statut", "simule"
                ])
            elif fichier == "offres_transfert":
                df = pd.DataFrame(columns=[
                    "id_offre", "id_joueur", "id_equipe_acheteur",
                    "id_equipe_vendeur", "montant", "date_offre",
                    "statut", "reponse_date"
                ])
            df.to_excel(path, index=False)

# --- Initialisation des données ---
init_data()

# --- Page d'inscription/Connexion ---
def page_inscription():
    st.title("🏆 Football Manager - Inscription")
    with st.form("inscription_form"):
        nom = st.text_input("Nom d'utilisateur")
        email = st.text_input("Email")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        id_equipe = st.selectbox(
            "Choisissez votre équipe",
            options=get_equipes()["id_equipe"].tolist(),
            format_func=lambda x: get_equipes().loc[get_equipes()["id_equipe"] == x, "nom"].values[0]
        )
        submitted = st.form_submit_button("S'inscrire")
        if submitted:
            if not nom or not email or not mot_de_passe:
                st.error("Veuillez remplir tous les champs.")
            else:
                # Vérifier si l'utilisateur existe déjà
                utilisateurs = load_data("utilisateurs")
                if not utilisateurs.empty and email in utilisateurs["email"].values:
                    st.error("Cet email est déjà utilisé.")
                else:
                    # Ajouter l'utilisateur
                    new_id = 1 if utilisateurs.empty else utilisateurs["id_utilisateur"].max() + 1
                    new_user = pd.DataFrame([{
                        "id_utilisateur": new_id,
                        "nom": nom,
                        "email": email,
                        "mot_de_passe": mot_de_passe,  # À chiffrer en production !
                        "id_equipe": id_equipe,
                        "date_inscription": datetime.now().strftime("%Y-%m-%d"),
                        "derniere_connexion": datetime.now().strftime("%Y-%m-%d")
                    }])
                    utilisateurs = pd.concat([utilisateurs, new_user], ignore_index=True)
                    save_data(utilisateurs, "utilisateurs")
                    st.success("Inscription réussie ! Vous pouvez maintenant vous connecter.")
                    st.session_state.page = "connexion"

def page_connexion():
    st.title("🏆 Football Manager - Connexion")
    with st.form("connexion_form"):
        email = st.text_input("Email")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")
        if submitted:
            utilisateurs = load_data("utilisateurs")
            user = utilisateurs[(utilisateurs["email"] == email) & (utilisateurs["mot_de_passe"] == mot_de_passe)]
            if not user.empty:
                st.session_state.user = user.iloc[0].to_dict()
                st.session_state.user["id_equipe"] = int(st.session_state.user["id_equipe"])
                st.session_state.page = "menu"
                st.experimental_rerun()
            else:
                st.error("Identifiants incorrects.")

# --- Page principale (Menu) ---
def page_menu():
    if "user" not in st.session_state:
        st.session_state.page = "connexion"
        st.experimental_rerun()
        return

    st.title(f"🏆 Football Manager - {st.session_state.user['nom']}")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Aller à",
        ["Équipe", "Calendrier", "Classement", "Ligue des Champions", "Marché des Transferts"]
    )

    if page == "Équipe":
        afficher_equipe()
    elif page == "Calendrier":
        afficher_calendrier()
    elif page == "Classement":
        afficher_classement()
    elif page == "Ligue des Champions":
        afficher_ligue_des_champions()
    elif page == "Marché des Transferts":
        afficher_marche_transferts()

def afficher_equipe():
    st.header("👥 Mon Équipe")
    equipe = get_equipes().loc[get_equipes()["id_equipe"] == st.session_state.user["id_equipe"]].iloc[0]
    st.subheader(f"{equipe['nom']} ({equipe['pays']} - {equipe['championnat']})")
    st.write(f"**Stade** : {equipe['stade']} ({equipe['capacite_stade']} places)")
    st.write(f"**Entraîneur** : {equipe['entraineur']}")
    st.write(f"**Budget transfert** : {equipe['budget_transfert']:,.0f} €")

    # Afficher les joueurs
    st.subheader("📋 Effectif")
    joueurs = get_joueurs_by_equipe(st.session_state.user["id_equipe"])
    if joueurs.empty:
        st.warning("Aucun joueur dans cette équipe.")
    else:
        # Filtre par poste
        poste_filter = st.selectbox(
            "Filtrer par poste",
            options=["Tous"] + joueurs["poste"].unique().tolist()
        )
        if poste_filter != "Tous":
            joueurs = joueurs[joueurs["poste"] == poste_filter]

        # Affichage sous forme de tableau
        st.dataframe(
            joueurs[["nom", "prenom", "poste", "age", "note_generale", "valeur_marche"]],
            hide_index=True
        )

    # Changer de tactique
    st.subheader("⚽ Tactique")
    tactiques = get_tactiques()
    tactique_choisie = st.selectbox(
        "Choisir une tactique",
        options=tactiques["id_tactique"].tolist(),
        format_func=lambda x: tactiques.loc[tactiques["id_tactique"] == x, "nom"].values[0]
    )
    st.write(f"**Formation** : {tactiques.loc[tactiques['id_tactique'] == tactique_choisie, 'formation'].values[0]}")

    # Afficher le terrain (simplifié)
    st.subheader("🗺️ Disposition des joueurs")
    terrain = """
    <div style="width: 600px; height: 400px; border: 2px solid green; position: relative; margin: 20px auto;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">⚽</div>
    </div>
    """
    st.markdown(terrain, unsafe_allow_html=True)
    st.info("*(Glisser-déposer des joueurs pour les positionner - À implémenter avec Streamlit + JavaScript)*")

def afficher_calendrier():
    st.header("📅 Calendrier")
    calendrier = get_calendrier()
    equipes = get_equipes()
    id_equipe = st.session_state.user["id_equipe"]

    # Filtrer les matchs de l'équipe de l'utilisateur
    matchs_equipe = calendrier[
        (calendrier["id_equipe_domicile"] == id_equipe) |
        (calendrier["id_equipe_exterieur"] == id_equipe)
    ]

    if matchs_equipe.empty:
        st.warning("Aucun match trouvé pour votre équipe.")
    else:
        st.subheader("Prochains matchs")
        for _, match in matchs_equipe.iterrows():
            equipe_domicile = equipes.loc[equipes["id_equipe"] == match["id_equipe_domicile"], "nom"].values[0]
            equipe_exterieur = equipes.loc[equipes["id_equipe"] == match["id_equipe_exterieur"], "nom"].values[0]
            statut = "✅ Terminé" if match["simule"] else "⏳ À venir"
            st.write(
                f"{match['date_match']} - {match['heure_match']} : "
                f"{equipe_domicile} vs {equipe_exterieur} - {statut}"
            )
            if not match["simule"]:
                if st.button(f"Simuler ce match (ID: {match['id_match']})"):
                    simuler_match(match["id_match"])
                    st.experimental_rerun()

def afficher_classement():
    st.header("🏆 Classements")
    championnats = get_championnats()
    championnat_choisi = st.selectbox(
        "Sélectionner un championnat",
        options=championnats["id_championnat"].tolist(),
        format_func=lambda x: championnats.loc[championnats["id_championnat"] == x, "nom"].values[0]
    )
    classement = get_classement(championnat_choisi)
    equipes = get_equipes()

    if classement.empty:
        st.warning("Aucun classement disponible.")
    else:
        # Fusionner avec les noms d'équipes
        classement_display = classement.merge(
            equipes[["id_equipe", "nom"]],
            left_on="id_equipe",
            right_on="id_equipe"
        )
        st.dataframe(
            classement_display[["position", "nom", "points", "victoires", "nuls", "defaites", "buts_pour", "buts_contre"]],
            hide_index=True
        )

def afficher_ligue_des_champions():
    st.header("🌍 Ligue des Champions")
    ldc = get_ligue_des_champions()
    matchs_ldc = get_matchs_ldc()
    equipes = get_equipes()

    if ldc.empty:
        st.warning("Aucune équipe qualifiée pour la Ligue des Champions.")
    else:
        st.subheader("Équipes qualifiées")
        st.dataframe(ldc.merge(equipes[["id_equipe", "nom", "pays"]], on="id_equipe"), hide_index=True)

        st.subheader("Matchs à venir")
        for _, match in matchs_ldc[~matchs_ldc["simule"]].iterrows():
            equipe_domicile = equipes.loc[equipes["id_equipe"] == match["id_equipe_domicile"], "nom"].values[0]
            equipe_exterieur = equipes.loc[equipes["id_equipe"] == match["id_equipe_exterieur"], "nom"].values[0]
            st.write(
                f"{match['date_match']} - {match['phase']} (Groupe {match['groupe']}) : "
                f"{equipe_domicile} vs {equipe_exterieur}"
            )
            if st.button(f"Simuler ce match (LDC ID: {match['id_match_ldc']})"):
                # À implémenter : Simulation d'un match de LDC
                st.warning("Fonctionnalité à implémenter.")

def afficher_marche_transferts():
    st.header("💰 Marché des Transferts")
    today = datetime.now()
    if today.month < 7 or today.month > 8:
        st.warning("Le marché des transferts est fermé (juillet-août uniquement).")
        return

    # Vendre un joueur
    st.subheader("🔄 Vendre un joueur")
    joueurs = get_joueurs_by_equipe(st.session_state.user["id_equipe"])
    if not joueurs.empty:
        joueur_a_vendre = st.selectbox(
            "Sélectionner un joueur à vendre",
            options=joueurs["id_joueur"].tolist(),
            format_func=lambda x: f"{joueurs.loc[joueurs['id_joueur'] == x, 'nom'].values[0]} {joueurs.loc[joueurs['id_joueur'] == x, 'prenom'].values[0]} ({joueurs.loc[joueurs['id_joueur'] == x, 'poste'].values[0]})"
        )
        prix = st.number_input("Prix de vente (€)", min_value=1_000_000, step=1_000_000)
        if st.button("Proposer à la vente"):
            # Ajouter une offre (l'équipe de l'utilisateur est la vendeuse)
            offres = load_data("offres_transfert")
            new_id = 1 if offres.empty else offres["id_offre"].max() + 1
            new_offre = pd.DataFrame([{
                "id_offre": new_id,
                "id_joueur": joueur_a_vendre,
                "id_equipe_acheteur": -1,  # -1 = Offre ouverte à tous
                "id_equipe_vendeur": st.session_state.user["id_equipe"],
                "montant": prix,
                "date_offre": datetime.now().strftime("%Y-%m-%d"),
                "statut": "En attente",
                "reponse_date": None
            }])
            offres = pd.concat([offres, new_offre], ignore_index=True)
            save_data(offres, "offres_transfert")
            st.success("Offre de vente ajoutée !")

    # Acheter un joueur
    st.subheader("🛒 Acheter un joueur")
    offres = get_offres_transfert()
    offres_acheteur = offres[offres["id_equipe_vendeur"] != st.session_state.user["id_equipe"]]
    if offres_acheteur.empty:
        st.info("Aucune offre disponible pour le moment.")
    else:
        for _, offre in offres_acheteur.iterrows():
            joueur = get_joueurs_by_equipe(offre["id_equipe_vendeur"]).loc[
                get_joueurs_by_equipe(offre["id_equipe_vendeur"])["id_joueur"] == offre["id_joueur"]
            ].iloc[0]
            equipe_vendeuse = get_equipes().loc[get_equipes()["id_equipe"] == offre["id_equipe_vendeur"], "nom"].values[0]
            st.write(
                f"👤 {joueur['nom']} {joueur['prenom']} ({joueur['poste']}) - "
                f"Équipe : {equipe_vendeuse} - Prix : {offre['montant']:,.0f} €"
            )
            if st.button(f"Faire une offre pour {joueur['nom']}"):
                contre_offre = st.number_input(
                    f"Montant de votre offre (€)",
                    min_value=offre["montant"] + 1_000_000,
                    step=1_000_000,
                    key=f"offre_{offre['id_offre']}"
                )
                if st.button(f"Envoyer l'offre pour {joueur['nom']}"):
                    # Ajouter une contre-offre
                    new_id = 1 if offres.empty else offres["id_offre"].max() + 1
                    new_offre = pd.DataFrame([{
                        "id_offre": new_id,
                        "id_joueur": offre["id_joueur"],
                        "id_equipe_acheteur": st.session_state.user["id_equipe"],
                        "id_equipe_vendeur": offre["id_equipe_vendeur"],
                        "montant": contre_offre,
                        "date_offre": datetime.now().strftime("%Y-%m-%d"),
                        "statut": "En attente",
                        "reponse_date": None
                    }])
                    offres = pd.concat([offres, new_offre], ignore_index=True)
                    save_data(offres, "offres_transfert")
                    st.success("Offre envoyée !")

    # Générer des offres IA (pour les autres clubs)
    if st.button("Simuler une journée de mercato (IA)"):
        generer_offres_ia()
        st.success("Offres IA générées !")

# --- Gestion des pages ---
if "page" not in st.session_state:
    st.session_state.page = "connexion"

if st.session_state.page == "connexion":
    page_connexion()
elif st.session_state.page == "inscription":
    page_inscription()
elif st.session_state.page == "menu":
    page_menu()