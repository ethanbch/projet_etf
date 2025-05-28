"""
Module de visualisation utilisant Streamlit.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import List

from helpers_analysis import (
    calculate_returns, calculate_cumulative_returns,
    calculate_volatility, normalize_prices
)


def display_etf_analysis(df: pd.DataFrame, ticker: str):
    """Affiche l'analyse d'un ETF individuel."""
    st.subheader(f"Analyse de {ticker}")
    
    # Filtrer les données pour l'ETF sélectionné
    etf_data = df[df['ticker'] == ticker].copy()
    etf_data.set_index('date', inplace=True)
    
    # Graphique des prix
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=etf_data.index,
        y=etf_data['close'],
        mode='lines',
        name='Prix de clôture'
    ))
    st.plotly_chart(fig)
    
    # Métriques clés
    col1, col2, col3 = st.columns(3)
    
    returns = calculate_returns(etf_data['close'])
    cum_returns = calculate_cumulative_returns(etf_data['close'])
    volatility = calculate_volatility(returns)
    
    with col1:
        st.metric(
            "Rendement total",
            f"{cum_returns.iloc[-1]:.2%}"
        )
    with col2:
        st.metric(
            "Rendement annualisé",
            f"{returns.mean() * 252:.2%}"
        )
    with col3:
        st.metric(
            "Volatilité annualisée",
            f"{volatility.iloc[-1]:.2%}"
        )


def display_etf_comparison(df: pd.DataFrame, tickers: List[str]):
    """Affiche la comparaison entre plusieurs ETF."""
    st.subheader("Comparaison des ETF")
    
    # Normalisation des prix
    normalized = normalize_prices(df, tickers)
    
    # Graphique comparatif
    fig = go.Figure()
    for ticker in tickers:
        fig.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized[ticker],
            mode='lines',
            name=ticker
        ))
    fig.update_layout(title="Performance relative (base 100)")
    st.plotly_chart(fig)
    
    # Tableau comparatif
    comparison_data = []
    for ticker in tickers:
        etf_data = df[df['ticker'] == ticker]['close']
        returns = calculate_returns(etf_data)
        cum_returns = calculate_cumulative_returns(etf_data)
        volatility = calculate_volatility(returns)
        
        comparison_data.append({
            'ETF': ticker,
            'Rendement total': f"{cum_returns.iloc[-1]:.2%}",
            'Volatilité': f"{volatility.iloc[-1]:.2%}"
        })
    
    st.table(pd.DataFrame(comparison_data))