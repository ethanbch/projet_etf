import time

import pandas as pd

from config_loader import load_config
from etl import process_all_etfs
from repository import EtfRepository


def main():
    print("--- Démarrage du processus ETL ---")

    # Chargement de la configuration
    print("Chargement de la configuration...")
    config = load_config()
    if not config:
        print("Erreur: Impossible de charger la configuration. Arrêt de l'ETL.")
        return

    # Initialisation du repository
    print("Initialisation du repository de base de données...")
    repository = EtfRepository(config)

    # Supprimer les anciennes tables
    repository.drop_tables_if_exist()
    # Réinitialiser la structure de la base de données avec les nouvelles tables
    repository.init_database()

    # Extraction et transformation des données
    print("Lancement de l'extraction et de la transformation des données ETF...")
    # process_all_etfs retourne maintenant df_metadata et une LISTE de df_prices
    df_metadata, list_of_df_prices = process_all_etfs(config)

    # Sauvegarde des métadonnées (une seule fois)
    if not df_metadata.empty:
        print("Sauvegarde des métadonnées...")
        repository.save_etf_metadata(df_metadata)
    else:
        print("Aucune métadonnée à sauvegarder.")

    # Sauvegarde des données de prix
    if list_of_df_prices:  # S'assurer que la liste n'est pas vide
        print(
            f"Préparation pour la sauvegarde des données de prix pour {len(list_of_df_prices)} ETF(s)..."
        )
        # Concaténer tous les dataframes de prix en un seul pour une insertion unique (plus efficace)
        all_prices_concatenated = pd.concat(list_of_df_prices, ignore_index=True)
        if not all_prices_concatenated.empty:
            print("Sauvegarde des données de prix concaténées...")
            repository.save_etf_prices(all_prices_concatenated)
        else:
            print(
                "Le DataFrame de prix concaténé est vide. Aucune donnée de prix sauvegardée."
            )
    else:
        print(
            "Aucune donnée de prix à sauvegarder (la liste des DataFrames de prix est vide)."
        )

    print("--- ETL terminé avec succès. ---")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Temps total d'exécution de l'ETL : {end_time - start_time:.2f} secondes.")
