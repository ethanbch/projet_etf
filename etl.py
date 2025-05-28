"""
Module ETL pour l'extraction et la transformation des données d'ETF.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List, Dict

from config_loader import Config, EtfConfig


def extract_etf_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Extrait les données historiques d'un ETF depuis Yahoo Finance."""
    etf = yf.Ticker(ticker)
    df = etf.history(start=start_date, end=end_date)
    
    if df.empty:
        print(f"Attention : Aucune donnée trouvée pour {ticker}")
        return pd.DataFrame()
        
    return df


def transform_etf_data(df: pd.DataFrame, etf_info: EtfConfig) -> pd.DataFrame:
    """Transforme les données brutes en format standardisé."""
    if df.empty:
        return df
        
    # Reset index pour avoir la date comme colonne
    df = df.reset_index()
    
    # Standardisation des noms de colonnes
    df = df.rename(columns={
        'Date': 'date',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Ajout des informations de l'ETF
    df['ticker'] = etf_info['ticker']
    df['name'] = etf_info['name']
    df['theme'] = etf_info['theme']
    
    return df


def process_all_etfs(config: Config) -> Dict[str, pd.DataFrame]:
    """Traite tous les ETF configurés."""
    start_date = config['date_range']['start']
    end_date = config['date_range']['end']
    
    results = {}
    for etf in config['etfs']:
        print(f"Extraction des données pour {etf['ticker']}...")
        raw_data = extract_etf_data(etf['ticker'], start_date, end_date)
        
        if not raw_data.empty:
            processed_data = transform_etf_data(raw_data, etf)
            results[etf['ticker']] = processed_data
            
    return results