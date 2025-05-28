"""
Module contenant les fonctions d'analyse pour les ETF.
"""

from datetime import datetime, timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd


def get_date_range(period: str) -> Tuple[datetime, datetime]:
    """Calcule les dates de début et fin en fonction de la période sélectionnée.
    Supporte les périodes : 1m, 3m, 6m, YTD, 1a, 3a, 5a, MAX.

    :param period: Le code de la période (ex: '1m' pour 1 mois)
    :type period: str
    :return: Un tuple contenant (date_début, date_fin)
    :rtype: Tuple[datetime, datetime]
    """
    end_date = datetime.now()
    start_date = end_date

    if period == "1m":
        start_date = end_date - timedelta(days=30)
    elif period == "3m":
        start_date = end_date - timedelta(days=90)
    elif period == "6m":
        start_date = end_date - timedelta(days=180)
    elif period == "YTD":
        start_date = datetime(end_date.year, 1, 1)
    elif period == "1a":
        start_date = end_date - timedelta(days=365)
    elif period == "3a":
        start_date = end_date - timedelta(days=365 * 3)
    elif period == "5a":
        start_date = end_date - timedelta(days=365 * 5)
    elif period == "MAX":
        start_date = datetime(2010, 1, 1)

    return start_date, end_date


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calcule les rendements journaliers d'une série de prix.

    :param prices: Série temporelle des prix de clôture
    :type prices: pd.Series
    :return: Série des rendements journaliers
    :rtype: pd.Series
    """
    return prices.pct_change()


def calculate_cumulative_returns(prices: pd.Series) -> pd.Series:
    """Calcule les rendements cumulés à partir d'une série de prix.
    La fonction utilise la formule (1 + r1)(1 + r2)...(1 + rn) - 1.

    :param prices: Série temporelle des prix de clôture
    :type prices: pd.Series
    :return: Série des rendements cumulés
    :rtype: pd.Series
    """
    returns = calculate_returns(prices)
    return (1 + returns).cumprod() - 1


def calculate_volatility(returns: pd.Series, window: int = 252) -> pd.Series:
    """Calcule la volatilité glissante annualisée des rendements.

    :param returns: Série des rendements journaliers
    :type returns: pd.Series
    :param window: Fenêtre de calcul en jours (252 jours = 1 an boursier)
    :type window: int
    :return: Série de la volatilité glissante annualisée
    :rtype: pd.Series
    """
    return returns.rolling(window=window).std() * np.sqrt(window)


def calculate_sharpe_ratio(
    returns: pd.Series, risk_free_rate: float = 0.02, window: int = 252
) -> pd.Series:
    """Calcule le ratio de Sharpe glissant, qui mesure le rendement excédentaire par unité de risque.

    :param returns: Série des rendements journaliers
    :type returns: pd.Series
    :param risk_free_rate: Taux sans risque annuel (par défaut 2%)
    :type risk_free_rate: float
    :param window: Fenêtre de calcul en jours (252 jours = 1 an boursier)
    :type window: int
    :return: Série du ratio de Sharpe glissant
    :rtype: pd.Series
    """
    excess_returns = returns - risk_free_rate / window
    return (excess_returns.rolling(window=window).mean() * window) / (
        returns.rolling(window=window).std() * np.sqrt(window)
    )


def calculate_sortino_ratio(
    returns: pd.Series, risk_free_rate: float = 0.02, window: int = 252
) -> pd.Series:
    """Calcule le ratio de Sortino glissant, qui mesure le rendement excédentaire par unité de risque baissier.

    :param returns: Série des rendements journaliers
    :type returns: pd.Series
    :param risk_free_rate: Taux sans risque annuel (par défaut 2%)
    :type risk_free_rate: float
    :param window: Fenêtre de calcul en jours (252 jours = 1 an boursier)
    :type window: int
    :return: Série du ratio de Sortino glissant
    :rtype: pd.Series
    """
    excess_returns = returns - risk_free_rate / window
    downside_returns = returns.copy()
    downside_returns[downside_returns > 0] = 0
    downside_std = downside_returns.rolling(window=window).std() * np.sqrt(window)
    return (excess_returns.rolling(window=window).mean() * window) / downside_std


def calculate_max_drawdown(prices: pd.Series) -> float:
    """Calcule le drawdown (perte maximale) à partir des prix historiques.
    Le drawdown mesure la perte en pourcentage depuis le plus haut historique.

    :param prices: Série temporelle des prix de clôture
    :type prices: pd.Series
    :return: Série des drawdowns en pourcentage
    :rtype: pd.Series
    """
    rolling_max = prices.expanding().max()
    drawdowns = prices / rolling_max - 1
    return drawdowns.min()


def normalize_prices(df: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
    """Normalise les prix de plusieurs ETF pour permettre une comparaison visuelle.
    Les prix sont indexés à 100 à la première date pour faciliter la comparaison de performance.

    :param df: DataFrame contenant les données de prix avec colonnes 'date', 'ticker' et 'close'
    :type df: pd.DataFrame
    :param tickers: Liste des codes des ETF à normaliser
    :type tickers: List[str]
    :return: DataFrame avec les prix normalisés, indexé par date avec une colonne par ETF
    :rtype: pd.DataFrame
    """
    df = df.sort_values(
        "date"
    )  # S'assure que les données sont dans l'ordre chronologique
    normalized = pd.DataFrame()

    for ticker in tickers:
        ticker_data = df[df["ticker"] == ticker][["date", "close"]].copy()
        ticker_data.set_index("date", inplace=True)
        ticker_data = ticker_data / ticker_data.iloc[0] * 100
        normalized[ticker] = ticker_data["close"]

    return normalized


def calculate_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la matrice de corrélation des rendements entre les différents ETF.

    :param returns_df: DataFrame contenant les données de prix avec colonnes 'date', 'ticker' et 'close'
    :type returns_df: pd.DataFrame
    :return: Matrice de corrélation des rendements entre les ETF
    :rtype: pd.DataFrame
    """
    return returns_df.pivot(columns="ticker", values="close").pct_change().corr()
