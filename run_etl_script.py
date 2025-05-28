"""
Script principal pour l'exécution du processus ETL.
"""

from config_loader import load_config
from etl import process_all_etfs
from repository import EtfRepository


def main():
    print("Démarrage de l'ETL...")
    
    # Chargement de la configuration
    config = load_config()
    
    # Initialisation du repository
    repository = EtfRepository(config)
    
    # Extraction et transformation des données
    print("Récupération des données depuis Yahoo Finance...")
    etf_data = process_all_etfs(config)
    
    # Sauvegarde dans la base de données
    print("Sauvegarde des données dans la base...")
    for ticker, df in etf_data.items():
        if not df.empty:
            repository.save_etf_data(df)
    
    print("ETL terminé avec succès.")


if __name__ == "__main__":
    main()