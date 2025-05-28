# etl.py

from datetime import datetime
from typing import Dict, List, Tuple 

import pandas as pd
import yfinance as yf

from config_loader import Config, EtfConfig 


def extract_etf_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Extrait les données historiques d'un ETF depuis Yahoo Finance."""
    print(f"  Tentative d'extraction pour {ticker} de {start_date} à {end_date}...")
    etf = yf.Ticker(ticker)
    try:
        df = etf.history(start=start_date, end=end_date)
        if df.empty:
            print(f"  Attention : Aucune donnée trouvée pour {ticker} pour la période spécifiée.")
            return pd.DataFrame()
        # S'assurer que l'index est bien datetime et sans timezone pour la compatibilité SQLite
        if isinstance(df.index, pd.DatetimeIndex):
            df.index = df.index.tz_localize(None)
        print(f"  Données extraites pour {ticker}: {len(df)} lignes.")
        return df
    except Exception as e:
        print(f"  Erreur lors de l'extraction pour {ticker}: {e}")
        return pd.DataFrame()


def transform_price_data(df_raw: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Transforme les données brutes de prix en format standardisé pour la table des prix."""
    if df_raw.empty:
        return pd.DataFrame()

    df = df_raw.reset_index().copy() 

    # Standardisation des noms de colonnes
    rename_map = {
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
        "Dividends": "dividends",
        "Stock Splits": "stock_splits",
    }
    df = df.rename(columns=rename_map)

    # Gérer l'absence de 'Capital Gains' qui est souvent problématique avec yfinance
    if "Capital Gains" in df_raw.columns: # Vérifier sur df_raw avant renommage car 'Capital Gains' peut ne pas être dans rename_map
        df["capital_gains"] = df_raw["Capital Gains"]
    elif "capital_gains" not in df.columns: # Si elle n'a pas été créée par un autre moyen
        df["capital_gains"] = 0.0 

    df["ticker"] = ticker
    
    # Sélectionner uniquement les colonnes qui seront dans la table etf_prices
    # Assure-toi que ces noms de colonnes correspondent à ceux définis dans repository.py pour la table etf_prices
    price_columns = ["date", "ticker", "open", "high", "low", "close", "volume", "dividends", "stock_splits", "capital_gains"]
    
    # Garder seulement les colonnes existantes pour éviter les erreurs
    existing_price_columns = [col for col in price_columns if col in df.columns]
    
    return df[existing_price_columns]


def process_all_etfs(config: Config) -> Tuple[pd.DataFrame, List[pd.DataFrame]]:
    """
    Traite tous les ETF configurés.
    Retourne un DataFrame pour les métadonnées et une liste de DataFrames pour les prix.
    """
    start_date = config["date_range"]["start"]
    end_date = config["date_range"]["end"]

    all_metadata_list = []
    all_prices_dfs_list = []

    print(f"Début du traitement des ETFs configurés (de {start_date} à {end_date})...")
    for etf_config_item in config["etfs"]: # etf_config_item est un EtfConfig (TypedDict)
        ticker = etf_config_item["ticker"]
        
        # Préparation des métadonnées
        all_metadata_list.append({
            "ticker": ticker,
            "name": etf_config_item["name"],
            "theme": etf_config_item["theme"]
        })

        print(f"Traitement de {ticker}...")
        raw_data = extract_etf_data(ticker, start_date, end_date)

        if not raw_data.empty:
            price_data = transform_price_data(raw_data, ticker)
            if not price_data.empty:
                all_prices_dfs_list.append(price_data)
        else:
            # Déjà loggé dans extract_etf_data
            pass
            
    df_metadata = pd.DataFrame(all_metadata_list)
    return df_metadata, all_prices_dfs_list