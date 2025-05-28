"""
Module de gestion de la base de données pour le stockage des données ETF.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from typing import Optional, List

from config_loader import Config


class EtfRepository:
    def __init__(self, config: Config):
        db_path = Path(config['database']['path'])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.init_database()
    
    def init_database(self):
        """Initialise la structure de la base de données."""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS etf_data (
                    date DATE,
                    ticker TEXT,
                    name TEXT,
                    theme TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (date, ticker)
                )
            """))
            conn.commit()
    
    def save_etf_data(self, df: pd.DataFrame):
        """Sauvegarde les données d'un ETF dans la base."""
        df.to_sql('etf_data', self.engine, if_exists='append', index=False)
    
    def get_etf_data(self, ticker: str, start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> pd.DataFrame:
        """Récupère les données d'un ETF depuis la base."""
        query = "SELECT * FROM etf_data WHERE ticker = :ticker"
        
        if start_date:
            query += " AND date >= :start_date"
        if end_date:
            query += " AND date <= :end_date"
            
        params = {'ticker': ticker, 'start_date': start_date, 'end_date': end_date}
        return pd.read_sql(query, self.engine, params=params)
    
    def get_etf_by_theme(self, theme: str) -> pd.DataFrame:
        """Récupère tous les ETF d'un thème donné."""
        query = "SELECT * FROM etf_data WHERE theme = :theme"
        return pd.read_sql(query, self.engine, params={'theme': theme})
    
    def get_all_themes(self) -> List[str]:
        """Récupère la liste des thèmes disponibles."""
        query = "SELECT DISTINCT theme FROM etf_data"
        return pd.read_sql(query, self.engine)['theme'].tolist()