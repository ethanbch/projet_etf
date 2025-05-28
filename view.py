"""
Module de visualisation utilisant Streamlit.
"""

from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from helpers_analysis import (
    calculate_correlation_matrix,
    calculate_cumulative_returns,
    calculate_returns,
    calculate_volatility,
    normalize_prices,
)


def display_etf_analysis(df: pd.DataFrame, ticker: str):
    """Affiche l'analyse d'un ETF individuel."""
    st.subheader(f"Analyse de {ticker}")

    # Filtrer les données pour l'ETF sélectionné
    etf_data = df[df["ticker"] == ticker].copy()
    etf_data.set_index("date", inplace=True)

    # Graphique des prix
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=etf_data.index, y=etf_data["close"], mode="lines", name="Prix de clôture"
        )
    )
    fig.update_layout(title="Évolution du prix", xaxis_title="Date", yaxis_title="Prix")
    st.plotly_chart(fig)

    # Métriques clés
    col1, col2, col3 = st.columns(3)

    returns = calculate_returns(etf_data["close"])
    cum_returns = calculate_cumulative_returns(etf_data["close"])
    volatility = calculate_volatility(returns)

    with col1:
        st.metric("Rendement total", f"{cum_returns.iloc[-1]:.2%}")
    with col2:
        st.metric("Rendement annualisé", f"{returns.mean() * 252:.2%}")
    with col3:
        st.metric("Volatilité annualisée", f"{volatility.iloc[-1]:.2%}")


def display_etf_comparison(df: pd.DataFrame, tickers: List[str]):
    """Affiche la comparaison entre plusieurs ETF."""
    st.subheader("Comparaison des ETF")

    # Onglets pour différentes visualisations
    tab1, tab2, tab3 = st.tabs(["Performance relative", "Corrélations", "Métriques"])

    with tab1:
        # Normalisation des prix et graphique comparatif
        normalized = normalize_prices(df, tickers)

        fig = go.Figure()
        for ticker in tickers:
            fig.add_trace(
                go.Scatter(
                    x=normalized.index, y=normalized[ticker], mode="lines", name=ticker
                )
            )
        fig.update_layout(
            title="Performance relative (base 100)",
            xaxis_title="Date",
            yaxis_title="Performance",
        )
        st.plotly_chart(fig)

    with tab2:
        # Matrice de corrélation
        returns_df = df.pivot(columns="ticker", values="close").pct_change().dropna()
        corr_matrix = returns_df.corr()

        fig = px.imshow(
            corr_matrix,
            labels=dict(color="Corrélation"),
            color_continuous_scale="RdBu",
            aspect="auto",
        )
        fig.update_layout(title="Matrice de corrélation")
        st.plotly_chart(fig)

    with tab3:
        # Tableau comparatif des métriques
        comparison_data = []
        for ticker in tickers:
            etf_data = df[df["ticker"] == ticker]["close"]
            returns = calculate_returns(etf_data)
            cum_returns = calculate_cumulative_returns(etf_data)
            volatility = calculate_volatility(returns)

            comparison_data.append(
                {
                    "ETF": ticker,
                    "Rendement total": f"{cum_returns.iloc[-1]:.2%}",
                    "Rendement annualisé": f"{returns.mean() * 252:.2%}",
                    "Volatilité annualisée": f"{volatility.iloc[-1]:.2%}",
                }
            )

        st.table(pd.DataFrame(comparison_data))
