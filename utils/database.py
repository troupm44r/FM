import pandas as pd
import os

DATA_DIR = "data"

def load_data(filename):
    """Charge un fichier Excel dans un DataFrame."""
    path = os.path.join(DATA_DIR, f"{filename}.xlsx")
    if os.path.exists(path):
        return pd.read_excel(path)
    return pd.DataFrame()

def save_data(df, filename):
    """Sauvegarde un DataFrame dans un fichier Excel."""
    path = os.path.join(DATA_DIR, f"{filename}.xlsx")
    df.to_excel(path, index=False)

def get_equipes():
    """Récupère la liste des équipes."""
    return load_data("equipes")

def get_joueurs():
    """Récupère la liste des joueurs."""
    return load_data("joueurs")

def get_joueurs_by_equipe(id_equipe):
    """Récupère les joueurs d'une équipe."""
    joueurs = load_data("joueurs")
    return joueurs[joueurs["id_equipe"] == id_equipe]

def get_championnats():
    """Récupère la liste des championnats."""
    return load_data("championnats")

def get_classement(id_championnat):
    """Récupère le classement d'un championnat."""
    classements = load_data("classements")
    return classements[classements["id_championnat"] == id_championnat]

def get_calendrier():
    """Récupère le calendrier des matchs."""
    return load_data("calendrier")

def update_match(id_match, score_domicile, score_exterieur, simule=True):
    """Met à jour un match dans le calendrier."""
    calendrier = load_data("calendrier")
    calendrier.loc[calendrier["id_match"] == id_match, "score_domicile"] = score_domicile
    calendrier.loc[calendrier["id_match"] == id_match, "score_exterieur"] = score_exterieur
    calendrier.loc[calendrier["id_match"] == id_match, "simule"] = simule
    save_data(calendrier, "calendrier")

def get_tactiques():
    """Récupère la liste des tactiques."""
    return load_data("tactiques")

def get_postes():
    """Récupère la liste des postes."""
    return load_data("postes")

def update_tactique_joueur(id_equipe, id_joueur, id_poste, id_tactique, x, y):
    """Met à jour la position d'un joueur dans une tactique."""
    tactique_joueurs = load_data("tactique_joueurs")
    existing = tactique_joueurs[
        (tactique_joueurs["id_equipe"] == id_equipe) &
        (tactique_joueurs["id_joueur"] == id_joueur) &
        (tactique_joueurs["id_tactique"] == id_tactique)
    ]
    if not existing.empty:
        tactique_joueurs.loc[existing.index, "id_poste"] = id_poste
        tactique_joueurs.loc[existing.index, "position_x"] = x
        tactique_joueurs.loc[existing.index, "position_y"] = y
    else:
        new_entry = pd.DataFrame([{
            "id": tactique_joueurs["id"].max() + 1 if not tactique_joueurs.empty else 1,
            "id_equipe": id_equipe,
            "id_joueur": id_joueur,
            "id_poste": id_poste,
            "id_tactique": id_tactique,
            "position_x": x,
            "position_y": y
        }])
        tactique_joueurs = pd.concat([tactique_joueurs, new_entry], ignore_index=True)
    save_data(tactique_joueurs, "tactique_joueurs")

def get_utilisateur(id_utilisateur):
    """Récupère un utilisateur par son ID."""
    utilisateurs = load_data("utilisateurs")
    return utilisateurs[utilisateurs["id_utilisateur"] == id_utilisateur]

def add_utilisateur(nom, email, mot_de_passe, id_equipe):
    """Ajoute un nouvel utilisateur."""
    utilisateurs = load_data("utilisateurs")
    new_id = utilisateurs["id_utilisateur"].max() + 1 if not utilisateurs.empty else 1
    new_user = pd.DataFrame([{
        "id_utilisateur": new_id,
        "nom": nom,
        "email": email,
        "mot_de_passe": mot_de_passe,
        "id_equipe": id_equipe,
        "date_inscription": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "derniere_connexion": pd.Timestamp.now().strftime("%Y-%m-%d")
    }])
    utilisateurs = pd.concat([utilisateurs, new_user], ignore_index=True)
    save_data(utilisateurs, "utilisateurs")

def get_offres_transfert():
    """Récupère les offres de transfert."""
    return load_data("offres_transfert")

def add_offre_transfert(id_joueur, id_equipe_acheteur, id_equipe_vendeur, montant):
    """Ajoute une offre de transfert."""
    offres = load_data("offres_transfert")
    new_id = offres["id_offre"].max() + 1 if not offres.empty else 1
    new_offre = pd.DataFrame([{
        "id_offre": new_id,
        "id_joueur": id_joueur,
        "id_equipe_acheteur": id_equipe_acheteur,
        "id_equipe_vendeur": id_equipe_vendeur,
        "montant": montant,
        "date_offre": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "statut": "En attente",
        "reponse_date": None
    }])
    offres = pd.concat([offres, new_offre], ignore_index=True)
    save_data(offres, "offres_transfert")

def update_transfert(id_offre, statut, reponse_date=None):
    """Met à jour une offre de transfert."""
    offres = load_data("offres_transfert")
    offres.loc[offres["id_offre"] == id_offre, "statut"] = statut
    if reponse_date:
        offres.loc[offres["id_offre"] == id_offre, "reponse_date"] = reponse_date
    save_data(offres, "offres_transfert")

def get_ligue_des_champions():
    """Récupère les équipes qualifiées pour la Ligue des Champions."""
    return load_data("ligue_des_champions")

def get_matchs_ldc():
    """Récupère les matchs de la Ligue des Champions."""
    return load_data("matchs_ldc")