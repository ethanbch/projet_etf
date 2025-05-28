"""
Module de visualisation utilisant Streamlit.
"""

from typing import List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from helpers_analysis import (
    calculate_beta,
    calculate_cumulative_returns,
    calculate_max_drawdown,
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_tracking_error,
    calculate_volatility,
    normalize_prices,
)


def display_etf_analysis(df: pd.DataFrame, etf_label: str, risk_free_rate: float):
    """Affiche l'analyse d'un ETF individuel."""
    st.subheader(f"Analyse de {etf_label}")

    # Extraction du ticker du label
    ticker = etf_label.split(" - ")[0]

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
    col1, col2, col3, col4 = st.columns(4)

    returns = calculate_returns(etf_data["close"])
    cum_returns = calculate_cumulative_returns(etf_data["close"])
    volatility = calculate_volatility(returns)
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate).iloc[-1]

    with col1:
        st.metric("Rendement total", f"{cum_returns.iloc[-1]:.2%}")
    with col2:
        st.metric("Rendement annualisé", f"{returns.mean() * 252:.2%}")
    with col3:
        st.metric("Volatilité annualisée", f"{volatility.iloc[-1]:.2%}")
    with col4:
        st.metric("Ratio de Sharpe", f"{sharpe:.2f}")

    st.caption(
        "Pour le calcul du ratio de Sharpe et du rendement annualisé, il faut sélectionner une période d'au moins 1 an."
    )


def display_etf_comparison(df: pd.DataFrame, tickers: List[str], risk_free_rate: float):
    """Affiche la comparaison entre plusieurs ETF."""
    st.subheader("Comparaison des ETF")

    # Obtenir les noms complets des ETF
    etf_names = {
        ticker: df[df["ticker"] == ticker]["name"].iloc[0] for ticker in tickers
    }

    # Onglets pour différentes visualisations
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Performance relative",
            "Performance vs Volatilité",
            "Corrélations",
            "Métriques",
        ]
    )

    with tab1:
        # Normalisation des prix et graphique comparatif
        normalized = normalize_prices(df, tickers)

        fig = go.Figure()
        for ticker in tickers:
            fig.add_trace(
                go.Scatter(
                    x=normalized.index,
                    y=normalized[ticker],
                    mode="lines",
                    name=f"{ticker} - {etf_names[ticker]}",
                )
            )
        fig.update_layout(
            title="Performance relative (base 100)",
            xaxis_title="Date",
            yaxis_title="Performance",
        )
        st.plotly_chart(fig)

    with tab2:
        # Graphique Performance vs Volatilité
        risk_return_data = []
        for ticker in tickers:
            etf_data = df[df["ticker"] == ticker]["close"]
            returns = calculate_returns(etf_data)
            annualized_return = returns.mean() * 252
            annualized_volatility = returns.std() * np.sqrt(252)
            risk_return_data.append(
                {
                    "ETF": f"{ticker} - {etf_names[ticker]}",
                    "Volatilité annualisée (%)": annualized_volatility * 100,
                    "Rendement annualisé (%)": annualized_return * 100,
                }
            )

        risk_return_df = pd.DataFrame(risk_return_data)

        fig = px.scatter(
            risk_return_df,
            x="Volatilité annualisée (%)",
            y="Rendement annualisé (%)",
            text="ETF",
            title="Rendement vs Risque",
        )
        fig.update_traces(textposition="top center", marker=dict(size=12))
        fig.add_shape(
            type="line",
            x0=0,
            y0=0,
            x1=risk_return_df["Volatilité annualisée (%)"].max(),
            y1=0,
            line=dict(color="gray", dash="dash"),
        )
        st.plotly_chart(fig)

    with tab3:
        # Matrice de corrélation
        returns_df = df.pivot(columns="ticker", values="close").pct_change().dropna()
        corr_matrix = returns_df.corr()

        st.caption(
            "Une corrélation proche de 1 indique que les ETFs évoluent de manière similaire, proche de -1 de manière opposée, et proche de 0 de manière indépendante."
        )

        # Renommer les colonnes/index avec les noms complets
        corr_matrix.columns = [
            f"{ticker} - {etf_names[ticker]}" for ticker in corr_matrix.columns
        ]
        corr_matrix.index = corr_matrix.columns

        fig = px.imshow(
            corr_matrix,
            labels=dict(color="Corrélation"),
            color_continuous_scale="RdBu",
            aspect="auto",
        )
        fig.update_layout(title="Matrice de corrélation")
        st.plotly_chart(fig)

    with tab4:
        st.subheader("Métriques de comparaison")

        # Récupération des données du SPY pour le calcul du beta
        spy_data = df[df["ticker"] == "SPY"].copy()
        spy_data.set_index("date", inplace=True)
        spy_returns = calculate_returns(spy_data["close"])

        # Préparation des données pour le tableau
        metrics_data = []

        for ticker in tickers:
            etf_data = df[df["ticker"] == ticker].copy()
            etf_data.set_index("date", inplace=True)
            returns = calculate_returns(etf_data["close"])

            # Calcul des métriques
            volatility = calculate_volatility(returns).iloc[-1]
            sharpe = calculate_sharpe_ratio(returns, risk_free_rate).iloc[-1]
            sortino = calculate_sortino_ratio(returns, risk_free_rate).iloc[-1]
            max_dd = calculate_max_drawdown(etf_data["close"])
            beta = calculate_beta(returns, spy_returns).iloc[-1]
            tracking_error = calculate_tracking_error(returns, spy_returns).iloc[-1]
            ann_return = returns.mean() * 252

            metrics_data.append(
                {
                    "ETF": f"{ticker} - {etf_names[ticker]}",
                    "Rendement annualisé": f"{ann_return:.2%}",
                    "Volatilité": f"{volatility:.2%}",
                    "Ratio de Sharpe": f"{sharpe:.2f}",
                    "Ratio de Sortino": f"{sortino:.2f}",
                    "Drawdown Max": f"{max_dd:.2%}",
                    "Beta vs SPY": f"{beta:.2f}",
                    "Tracking Error": f"{tracking_error:.2%}",
                }
            )

        # Affichage du tableau des métriques
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df.set_index("ETF"), use_container_width=True)

        # Légende des métriques
        st.caption(
            """
        - Rendement annualisé : performance moyenne sur un an
        - Volatilité : mesure de la variation des rendements
        - Ratio de Sharpe : rendement ajusté du risque (> 1 est bon)
        - Ratio de Sortino : comme Sharpe mais ne pénalise que les pertes
        - Drawdown Max : perte maximale sur la période
        - Beta vs SPY : sensibilité aux mouvements du S&P 500 (1 = même sensibilité)
        - Tracking Error : écart de suivi par rapport au S&P 500
        - Si certaines métriques sont NaN, essayer de bouger la période et/ou le taux sans risque.
        """
        )
