"""
Module contenant les fonctions d'analyse pour les ETF.
"""

import pandas as pd
import numpy as np
from typing import List


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


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02,
                         window: int = 252) -> pd.Series:
    """Calcule le ratio de Sharpe glissant."""
    excess_returns = returns - risk_free_rate/window
    return (excess_returns.rolling(window=window).mean() * window) / \
           (returns.rolling(window=window).std() * np.sqrt(window))


def normalize_prices(df: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
    """Normalise les prix de plusieurs ETF pour comparaison."""
    normalized = pd.DataFrame(index=df.index)
    for ticker in tickers:
        price_data = df[df['ticker'] == ticker]['close']
        normalized[ticker] = price_data / price_data.iloc[0] * 100
    return normalized


def calculate_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la matrice de corrélation entre les ETF."""
    return returns_df.pivot(columns='ticker', values='close').pct_change().corr()