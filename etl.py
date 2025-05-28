"""
Module ETL pour la gestion des données d'ETF.
Gère l'extraction des données depuis Yahoo Finance, leur transformation
et leur chargement dans la base de données SQLite.
"""

from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
import yfinance as yf

from config_loader import Config, EtfConfig


def extract_etf_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Extrait les données historiques d'un ETF depuis Yahoo Finance.

    :param ticker: Code de l'ETF (ex: 'SPY' pour SPDR S&P 500)
    :type ticker: str
    :param start_date: Date de début au format 'YYYY-MM-DD'
    :type start_date: str
    :param end_date: Date de fin au format 'YYYY-MM-DD'
    :type end_date: str
    :return: DataFrame contenant l'historique des prix
    :rtype: pd.DataFrame
    :raises: Exception si l'extraction échoue
    """
    print(f"  Tentative d'extraction pour {ticker} de {start_date} à {end_date}...")
    etf = yf.Ticker(ticker)
    try:
        df = etf.history(start=start_date, end=end_date)
        if df.empty:
            print(
                f"  Attention : Aucune donnée trouvée pour {ticker} pour la période spécifiée."
            )
            return pd.DataFrame()
        if isinstance(df.index, pd.DatetimeIndex):
            df.index = df.index.tz_localize(None)
        print(f"  Données extraites pour {ticker}: {len(df)} lignes.")
        return df
    except Exception as e:
        print(f"  Erreur lors de l'extraction pour {ticker}: {e}")
        return pd.DataFrame()


def transform_price_data(df_raw: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Transforme les données brutes de prix en format standardisé.

    Normalise les noms de colonnes et assure la présence de toutes
    les colonnes requises avec des valeurs par défaut si nécessaire.

    :param df_raw: DataFrame brut extrait de Yahoo Finance
    :type df_raw: pd.DataFrame
    :param ticker: Code de l'ETF
    :type ticker: str
    :return: DataFrame standardisé avec colonnes normalisées
    :rtype: pd.DataFrame
    """
    if df_raw.empty:
        return pd.DataFrame()

    df = df_raw.reset_index().copy()

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
    if (
        "Capital Gains" in df_raw.columns
    ):  # Vérifier sur df_raw avant renommage car 'Capital Gains' peut ne pas être dans rename_map
        df["capital_gains"] = df_raw["Capital Gains"]
    elif (
        "capital_gains" not in df.columns
    ):  # Si elle n'a pas été créée par un autre moyen
        df["capital_gains"] = 0.0

    df["ticker"] = ticker

    # Sélectionner uniquement les colonnes qui seront dans la table etf_prices
    price_columns = [
        "date",
        "ticker",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "dividends",
        "stock_splits",
        "capital_gains",
    ]

    # On garde seulement les colonnes existantes pour éviter les erreurs
    existing_price_columns = [col for col in price_columns if col in df.columns]

    return df[existing_price_columns]


def process_all_etfs(config: Config) -> Tuple[pd.DataFrame, List[pd.DataFrame]]:
    """Traite tous les ETF configurés dans le fichier config.yaml.

    Extrait les données de chaque ETF, les transforme et prépare
    les DataFrames pour le chargement dans la base de données.

    :param config: Configuration chargée depuis config.yaml
    :type config: Config
    :return: Tuple contenant (DataFrame des métadonnées, Liste des DataFrames de prix)
    :rtype: Tuple[pd.DataFrame, List[pd.DataFrame]]
    """
    start_date = config["date_range"]["start"]
    end_date = config["date_range"]["end"]

    all_metadata_list = []
    all_prices_dfs_list = []

    print(f"Début du traitement des ETFs configurés (de {start_date} à {end_date})...")
    for etf_config_item in config[
        "etfs"
    ]:  # etf_config_item est un EtfConfig (TypedDict)
        ticker = etf_config_item["ticker"]

        # Préparation des métadonnées
        all_metadata_list.append(
            {
                "ticker": ticker,
                "name": etf_config_item["name"],
                "theme": etf_config_item["theme"],
            }
        )

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
