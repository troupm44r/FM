import pandas as pd
import random
from datetime import datetime, timedelta
from utils.database import load_data, save_data, get_equipes, get_joueurs

def generer_offres_ia():
    """Génère des offres de transfert aléatoires pour les clubs IA."""
    equipes = load_data("equipes")
    joueurs = load_data("joueurs")
    offres = load_data("offres_transfert")

    # Sélectionner 10-20% des clubs pour faire une offre
    nb_clubs = len(equipes)
    nb_offres = random.randint(int(nb_clubs * 0.1), int(nb_clubs * 0.2))

    for _ in range(nb_offres):
        # Choisir un club acheteur (pas l'utilisateur)
        id_equipe_acheteur = random.choice(equipes[equipes["id_equipe"] != 1]["id_equipe"].tolist())

        # Choisir un joueur à acheter (pas dans son équipe)
        joueurs_disponibles = joueurs[joueurs["id_equipe"] != id_equipe_acheteur]
        if not joueurs_disponibles.empty:
            joueur = joueurs_disponibles.sample(1).iloc[0]
            id_joueur = joueur["id_joueur"]
            id_equipe_vendeur = joueur["id_equipe"]

            # Calculer un prix aléatoire (entre 50% et 150% de la valeur marchande)
            prix = int(joueur["valeur_marche"] * random.uniform(0.5, 1.5))

            # Vérifier si le club acheteur a assez de budget
            budget_acheteur = equipes.loc[equipes["id_equipe"] == id_equipe_acheteur, "budget_transfert"].values[0]
            if prix <= budget_acheteur:
                # Ajouter l'offre
                new_id = offres["id_offre"].max() + 1 if not offres.empty else 1
                new_offre = pd.DataFrame([{
                    "id_offre": new_id,
                    "id_joueur": id_joueur,
                    "id_equipe_acheteur": id_equipe_acheteur,
                    "id_equipe_vendeur": id_equipe_vendeur,
                    "montant": prix,
                    "date_offre": datetime.now().strftime("%Y-%m-%d"),
                    "statut": "En attente",
                    "reponse_date": None
                }])
                offres = pd.concat([offres, new_offre], ignore_index=True)
                save_data(offres, "offres_transfert")

def traiter_offre(id_offre, statut):
    """Traite une offre de transfert (acceptée/refusée)."""
    offres = load_data("offres_transfert")
    equipes = load_data("equipes")
    joueurs = load_data("joueurs")
    transferts = load_data("transferts")

    offre = offres[offres["id_offre"] == id_offre].iloc[0]
    id_joueur = offre["id_joueur"]
    id_equipe_acheteur = offre["id_equipe_acheteur"]
    id_equipe_vendeur = offre["id_equipe_vendeur"]
    montant = offre["montant"]

    if statut == "Acceptée":
        # Mettre à jour le joueur (nouvelle équipe)
        joueurs.loc[joueurs["id_joueur"] == id_joueur, "id_equipe"] = id_equipe_acheteur

        # Mettre à jour les budgets
        equipes.loc[equipes["id_equipe"] == id_equipe_acheteur, "budget_transfert"] -= montant
        equipes.loc[equipes["id_equipe"] == id_equipe_vendeur, "budget_transfert"] += montant

        # Ajouter au historique des transferts
        new_id = transferts["id_transfert"].max() + 1 if not transferts.empty else 1
        new_transfert = pd.DataFrame([{
            "id_transfert": new_id,
            "id_joueur": id_joueur,
            "id_equipe_ancienne": id_equipe_vendeur,
            "id_equipe_nouvelle": id_equipe_acheteur,
            "date_transfert": datetime.now().strftime("%Y-%m-%d"),
            "montant": montant,
            "type": "Achat",
            "duree_pret": None
        }])
        transferts = pd.concat([transferts, new_transfert], ignore_index=True)

        # Sauvegarder les modifications
        save_data(joueurs, "joueurs")
        save_data(equipes, "equipes")
        save_data(transferts, "transferts")

    # Mettre à jour le statut de l'offre
    offres.loc[offres["id_offre"] == id_offre, "statut"] = statut
    offres.loc[offres["id_offre"] == id_offre, "reponse_date"] = datetime.now().strftime("%Y-%m-%d")
    save_data(offres, "offres_transfert")