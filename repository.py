# repository.py

from pathlib import Path
from typing import List, Optional

import pandas as pd
from sqlalchemy import create_engine, text

from config_loader import Config # Assure-toi que Config est bien défini


class EtfRepository:
    def __init__(self, config: Config):
        db_path_str = config["database"]["path"] 
        db_path = Path(db_path_str)
        db_path.parent.mkdir(parents=True, exist_ok=True) # Crée le dossier 'data' si besoin
        self.engine = create_engine(f"sqlite:///{db_path.resolve()}") # resolve() pour un chemin absolu
        print(f"Moteur de base de données initialisé pour : {db_path.resolve()}")
        # L'initialisation de la DB (création des tables) sera faite par le script ETL.

    def drop_tables_if_exist(self):
        """Supprime les tables si elles existent (pour une réinitialisation propre de l'ETL)."""
        with self.engine.connect() as conn:
            print("Tentative de suppression des tables 'etf_prices' et 'etf_metadata'...")
            conn.execute(text("DROP TABLE IF EXISTS etf_prices"))
            conn.execute(text("DROP TABLE IF EXISTS etf_metadata"))
            conn.commit()
            print("Tables 'etf_prices' et 'etf_metadata' supprimées (si elles existaient).")

    def init_database(self):
        """Initialise la structure des DEUX tables de la base de données."""
        with self.engine.connect() as conn:
            print("Initialisation des tables 'etf_metadata' et 'etf_prices'...")
            # Table pour les métadonnées
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS etf_metadata (
                        ticker TEXT PRIMARY KEY,
                        name TEXT,
                        theme TEXT
                    )
                    """
                )
            )
            # Table pour les données de prix
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS etf_prices (
                        date TEXT, -- Stocker comme TEXT au format YYYY-MM-DD
                        ticker TEXT,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        dividends REAL,
                        stock_splits REAL,
                        capital_gains REAL,
                        PRIMARY KEY (date, ticker),
                        FOREIGN KEY (ticker) REFERENCES etf_metadata (ticker)
                    )
                    """
                )
            )
            conn.commit()
        print("Tables 'etf_metadata' et 'etf_prices' initialisées (ou déjà existantes).")

    def save_etf_metadata(self, df_metadata: pd.DataFrame):
        """Sauvegarde les métadonnées des ETF dans la base."""
        if not df_metadata.empty:
            try:
                df_metadata.to_sql("etf_metadata", self.engine, if_exists="replace", index=False)
                print(f"{len(df_metadata)} lignes de métadonnées sauvegardées/remplacées dans 'etf_metadata'.")
            except Exception as e:
                print(f"Erreur lors de la sauvegarde des métadonnées : {e}")
        else:
            print("Aucune métadonnée à sauvegarder.")

    def save_etf_prices(self, df_prices_all: pd.DataFrame): # Prend maintenant un seul grand DataFrame
        """Sauvegarde toutes les données de prix dans la base."""
        if not df_prices_all.empty:
            try:
                # S'assurer que la colonne date est au format TEXT YYYY-MM-DD
                if 'date' in df_prices_all.columns:
                    df_prices_all['date'] = pd.to_datetime(df_prices_all['date']).dt.strftime('%Y-%m-%d')
                
                # Remplacer toute la table des prix pour éviter les doublons et simplifier l'ETL
                df_prices_all.to_sql("etf_prices", self.engine, if_exists="replace", index=False)
                print(f"{len(df_prices_all)} lignes de prix au total sauvegardées/remplacées dans 'etf_prices'.")
            except Exception as e:
                print(f"Erreur lors de la sauvegarde des données de prix : {e}")
        else:
            print("Aucune donnée de prix à sauvegarder.")

    def get_etf_data(
        self,
        ticker: str,
        start_date_str: Optional[str] = None, # Renommé pour clarifier que c'est un string
        end_date_str: Optional[str] = None,   # Renommé
    ) -> pd.DataFrame:
        """
        Récupère les données d'un ETF depuis la base en joignant les prix et les métadonnées.
        La jointure est faite avec Pandas.
        """
        # 1. Récupérer les métadonnées
        query_metadata = "SELECT ticker, name, theme FROM etf_metadata WHERE ticker = :ticker_param"
        df_metadata = pd.read_sql(query_metadata, self.engine, params={"ticker_param": ticker})

        if df_metadata.empty:
            # print(f"Aucune métadonnée trouvée pour le ticker : {ticker}") # Peut être bruyant
            return pd.DataFrame()

        # 2. Récupérer les données de prix
        query_prices = "SELECT date, ticker, open, high, low, close, volume, dividends, stock_splits, capital_gains FROM etf_prices WHERE ticker = :ticker_param"
        params_prices = {"ticker_param": ticker}
        
        if start_date_str:
            query_prices += " AND date >= :start_date_param"
            params_prices["start_date_param"] = start_date_str
        if end_date_str:
            query_prices += " AND date <= :end_date_param"
            params_prices["end_date_param"] = end_date_str
        
        query_prices += " ORDER BY date ASC" 

        df_prices = pd.read_sql(query_prices, self.engine, params=params_prices)

        if df_prices.empty:
            # print(f"Aucune donnée de prix trouvée pour {ticker} dans la plage de dates spécifiée.") # Peut être bruyant
            return pd.DataFrame()
        
        # Convertir la colonne date en objet datetime de Pandas après lecture
        if 'date' in df_prices.columns:
            df_prices['date'] = pd.to_datetime(df_prices['date'])

        # 3. Joindre avec Pandas
        combined_df = pd.merge(df_prices, df_metadata, on="ticker", how="left")
        
        return combined_df

    def get_all_etf_info_for_selection(self) -> pd.DataFrame:
        """Récupère ticker, name, theme pour tous les ETF (pour les selectbox)."""
        query = "SELECT ticker, name, theme FROM etf_metadata ORDER BY ticker ASC"
        return pd.read_sql(query, self.engine)

    def get_all_themes(self) -> List[str]:
        """Récupère la liste des thèmes disponibles."""
        query = "SELECT DISTINCT theme FROM etf_metadata WHERE theme IS NOT NULL AND theme != '' ORDER BY theme ASC"
        df_themes = pd.read_sql(query, self.engine)
        return df_themes["theme"].tolist() if not df_themes.empty else []