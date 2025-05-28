"""
Module contenant les fonctions d'analyse pour les ETF.
"""

from datetime import datetime, timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd


def get_date_range(period: str) -> Tuple[datetime, datetime]:
    """Calcule les dates de début et fin en fonction de la période sélectionnée."""
    end_date = datetime.now()
    start_date = end_date  # sera modifié ci-dessous

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
        start_date = datetime(2000, 1, 1)  # Une date suffisamment ancienne

    return start_date, end_date


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calcule les rendements journaliers."""
    return prices.pct_change()


def calculate_cumulative_returns(prices: pd.Series) -> pd.Series:
    """Calcule les rendements cumulés."""
    returns = calculate_returns(prices)
    return (1 + returns).cumprod() - 1


def calculate_volatility(returns: pd.Series, window: int = 252) -> pd.Series:
    """Calcule la volatilité glissante."""
    return returns.rolling(window=window).std() * np.sqrt(window)


def calculate_sharpe_ratio(
    returns: pd.Series, risk_free_rate: float = 0.02, window: int = 252
) -> pd.Series:
    """Calcule le ratio de Sharpe glissant."""
    excess_returns = returns - risk_free_rate / window
    return (excess_returns.rolling(window=window).mean() * window) / (
        returns.rolling(window=window).std() * np.sqrt(window)
    )


def calculate_sortino_ratio(
    returns: pd.Series, risk_free_rate: float = 0.02, window: int = 252
) -> pd.Series:
    """Calcule le ratio de Sortino glissant (comme Sharpe mais ne pénalise que la volatilité négative)."""
    excess_returns = returns - risk_free_rate / window
    downside_returns = returns.copy()
    downside_returns[downside_returns > 0] = 0
    downside_std = downside_returns.rolling(window=window).std() * np.sqrt(window)
    return (excess_returns.rolling(window=window).mean() * window) / downside_std


def calculate_max_drawdown(prices: pd.Series) -> float:
    """Calcule le drawdown maximum sur toute la période."""
    rolling_max = prices.expanding().max()
    drawdowns = prices / rolling_max - 1
    return drawdowns.min()


def calculate_beta(
    returns: pd.Series, market_returns: pd.Series, window: int = 252
) -> pd.Series:
    """Calcule le beta glissant par rapport au marché (SPY)."""
    covariance = returns.rolling(window=window).cov(market_returns)
    market_variance = market_returns.rolling(window=window).var()
    return covariance / market_variance


def calculate_tracking_error(
    returns: pd.Series, benchmark_returns: pd.Series, window: int = 252
) -> pd.Series:
    """Calcule l'erreur de suivi (tracking error) par rapport à un benchmark."""
    return (returns - benchmark_returns).rolling(window=window).std() * np.sqrt(window)


def normalize_prices(df: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
    """Normalise les prix de plusieurs ETF pour comparaison."""
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
    """Calcule la matrice de corrélation entre les ETF."""
    return returns_df.pivot(columns="ticker", values="close").pct_change().corr()


def calculate_sortino_ratio(
    returns: pd.Series, risk_free_rate: float = 0.02, window: int = 252
) -> pd.Series:
    """Calcule le ratio de Sortino glissant (comme Sharpe mais ne pénalise que la volatilité négative)."""
    excess_returns = returns - risk_free_rate / window
    downside_returns = returns.copy()
    downside_returns[downside_returns > 0] = 0
    downside_std = downside_returns.rolling(window=window).std() * np.sqrt(window)
    return (excess_returns.rolling(window=window).mean() * window) / downside_std


def calculate_max_drawdown(prices: pd.Series) -> float:
    """Calcule le drawdown maximum sur toute la période."""
    rolling_max = prices.expanding().max()
    drawdowns = prices / rolling_max - 1
    return drawdowns.min()


def calculate_beta(
    returns: pd.Series, market_returns: pd.Series, window: int = 252
) -> pd.Series:
    """Calcule le beta glissant par rapport au marché (SPY)."""
    covariance = returns.rolling(window=window).cov(market_returns)
    market_variance = market_returns.rolling(window=window).var()
    return covariance / market_variance


def calculate_tracking_error(
    returns: pd.Series, benchmark_returns: pd.Series, window: int = 252
) -> pd.Series:
    """Calcule l'erreur de suivi (tracking error) par rapport à un benchmark."""
    return (returns - benchmark_returns).rolling(window=window).std() * np.sqrt(window)
