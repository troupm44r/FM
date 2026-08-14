import pandas as pd
import random
from utils.database import load_data, save_data, update_match, get_classement, update_classement

def simuler_match(id_match):
    """Simule un match et met à jour les statistiques."""
    calendrier = load_data("calendrier")
    equipes = load_data("equipes")
    joueurs = load_data("joueurs")
    classements = load_data("classements")

    match = calendrier[calendrier["id_match"] == id_match].iloc[0]
    id_equipe_domicile = match["id_equipe_domicile"]
    id_equipe_exterieur = match["id_equipe_exterieur"]
    id_championnat = match["id_championnat"]

    # Récupérer les joueurs des deux équipes
    joueurs_domicile = joueurs[joueurs["id_equipe"] == id_equipe_domicile]
    joueurs_exterieur = joueurs[joueurs["id_equipe"] == id_equipe_exterieur]

    # Calculer la force d'attaque et de défense pour chaque équipe
    force_attaque_domicile = joueurs_domicile[["atq_finition", "atq_tir", "atq_passe", "atq_dribbles"]].mean().mean()
    force_defense_domicile = joueurs_domicile[["def_defense", "def_tacle", "def_interception", "def_aérien"]].mean().mean()
    force_attaque_exterieur = joueurs_exterieur[["atq_finition", "atq_tir", "atq_passe", "atq_dribbles"]].mean().mean()
    force_defense_exterieur = joueurs_exterieur[["def_defense", "def_tacle", "def_interception", "def_aérien"]].mean().mean()

    # Ajouter un bonus pour l'équipe à domicile
    force_attaque_domicile *= 1.1
    force_defense_domicile *= 1.05

    # Simuler le score (moyenne de 2-3 buts par match)
    buts_domicile = 0
    buts_exterieur = 0
    actions = random.randint(20, 30)  # Nombre d'actions dans le match

    for _ in range(actions):
        # Qui attaque ? (55% domicile, 45% extérieur)
        attaquant = "domicile" if random.random() < 0.55 else "exterieur"

        if attaquant == "domicile":
            # Probabilité de but = (Force attaque domicile) / (Force défense extérieur + 50) * 100
            prob_but = (force_attaque_domicile / (force_defense_exterieur + 50)) * 100
            if random.random() * 100 < prob_but:
                buts_domicile += 1
        else:
            prob_but = (force_attaque_exterieur / (force_defense_domicile + 50)) * 100
            if random.random() * 100 < prob_but:
                buts_exterieur += 1

    # Mise à jour du match
    update_match(id_match, buts_domicile, buts_exterieur, simule=True)

    # Mise à jour du classement
    classement = classements[(classements["id_championnat"] == id_championnat)]
    if not classement.empty:
        # Trouver les lignes des deux équipes
        ligne_domicile = classement[classement["id_equipe"] == id_equipe_domicile].index
        ligne_exterieur = classement[classement["id_equipe"] == id_equipe_exterieur].index

        if buts_domicile > buts_exterieur:
            # Victoire à domicile
            classement.loc[ligne_domicile, "points"] += 3
            classement.loc[ligne_domicile, "victoires"] += 1
            classement.loc[ligne_exterieur, "defaites"] += 1
        elif buts_domicile < buts_exterieur:
            # Victoire à l'extérieur
            classement.loc[ligne_exterieur, "points"] += 3
            classement.loc[ligne_exterieur, "victoires"] += 1
            classement.loc[ligne_domicile, "defaites"] += 1
        else:
            # Match nul
            classement.loc[ligne_domicile, "points"] += 1
            classement.loc[ligne_exterieur, "points"] += 1
            classement.loc[ligne_domicile, "nuls"] += 1
            classement.loc[ligne_exterieur, "nuls"] += 1

        # Mise à jour des buts
        classement.loc[ligne_domicile, "buts_pour"] += buts_domicile
        classement.loc[ligne_domicile, "buts_contre"] += buts_exterieur
        classement.loc[ligne_exterieur, "buts_pour"] += buts_exterieur
        classement.loc[ligne_exterieur, "buts_contre"] += buts_domicile

        # Mise à jour de la différence de buts
        classement.loc[ligne_domicile, "diff_buts"] = (
            classement.loc[ligne_domicile, "buts_pour"] -
            classement.loc[ligne_domicile, "buts_contre"]
        )
        classement.loc[ligne_exterieur, "diff_buts"] = (
            classement.loc[ligne_exterieur, "buts_pour"] -
            classement.loc[ligne_exterieur, "buts_contre"]
        )

        # Mise à jour des matchs joués
        classement.loc[ligne_domicile, "matchs_joues"] += 1
        classement.loc[ligne_exterieur, "matchs_joues"] += 1

        # Reclasser les équipes (par points, puis différence de buts)
        classement = classement.sort_values(
            by=["points", "diff_buts", "buts_pour"],
            ascending=[False, False, False]
        ).reset_index(drop=True)
        classement["position"] = classement.index + 1

        # Sauvegarder le classement
        save_data(classement, "classements")

    return f"Match simulé : {buts_domicile}-{buts_exterieur}"