"""
Module de visualisation utilisant Streamlit pour l'interface utilisateur de l'application ETF.
Fournit des fonctions pour afficher des analyses individuelles et des comparaisons d'ETF
avec des graphiques interactifs et des métriques financières.
"""

from typing import List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from helpers_analysis import (
    calculate_cumulative_returns,
    calculate_max_drawdown,
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_volatility,
    normalize_prices,
)


def display_etf_analysis(df: pd.DataFrame, etf_label: str, risk_free_rate: float):
    """Affiche l'analyse détaillée d'un ETF individuel avec graphiques et métriques.

    :param df: DataFrame contenant les données de l'ETF (prix, volume, etc.)
    :type df: pd.DataFrame
    :param etf_label: Label de l'ETF au format "TICKER - Nom"
    :type etf_label: str
    :param risk_free_rate: Taux sans risque utilisé pour les calculs de ratios
    :type risk_free_rate: float
    """
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
        """Pour les calculs avec une période inférieure à 1 an :        
        - Le rendement annualisé est une projection sur un an basée sur la performance observée     
        - La volatilité annualisée est ajustée en fonction de la longueur réelle de la période       
        - Le ratio de Sharpe utilise ces métriques ajustées pour rester cohérent        
    Plus la période est courte, plus ces projections sont hypothétiques.
    """
    )


def display_etf_comparison(df: pd.DataFrame, tickers: List[str], risk_free_rate: float):
    """Affiche une comparaison interactive entre plusieurs ETF.

    Inclut:
    - Performance relative (base 100)
    - Graphique risque/rendement
    - Matrice de corrélation
    - Tableau de métriques comparatives
    - Graphique radar des métriques normalisées

    :param df: DataFrame contenant les données de tous les ETF
    :type df: pd.DataFrame
    :param tickers: Liste des tickers des ETF à comparer
    :type tickers: List[str]
    :param risk_free_rate: Taux sans risque pour les calculs de ratios
    :type risk_free_rate: float
    """
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

    with tab3:  # Onglet "Corrélations"
        st.subheader("Matrice de Corrélation des Rendements")

        if df.empty or not tickers or len(tickers) < 2:
            st.warning(
                "Sélectionnez au moins deux ETFs avec des données pour la corrélation."
            )
        else:
            correlation_input_df = df[["date", "ticker", "close"]].copy()
            correlation_input_df["date"] = pd.to_datetime(correlation_input_df["date"])

            try:
                pivot_prices_df = correlation_input_df.pivot_table(
                    index="date", columns="ticker", values="close"
                )
                daily_returns_df = pivot_prices_df.pct_change().dropna(how="all")

                if daily_returns_df.empty or daily_returns_df.shape[1] < 2:
                    st.warning(
                        "Pas assez de données de rendements pour la corrélation."
                    )
                else:
                    corr_matrix = daily_returns_df.corr()
                    labels_for_matrix = corr_matrix.columns.tolist()

                    corr_matrix_for_display = corr_matrix.copy()
                    corr_matrix_for_display.columns = labels_for_matrix
                    corr_matrix_for_display.index = labels_for_matrix

                    fig_corr = px.imshow(
                        corr_matrix_for_display,
                        labels=dict(color="Corrélation"),
                        text_auto=".2f",
                        color_continuous_scale="RdBu",
                        zmin=-1,
                        zmax=1,
                        aspect="auto",
                    )
                    fig_corr.update_layout(title_text="Matrice de Corrélation")
                    st.plotly_chart(fig_corr, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur lors du calcul de la corrélation : {e}")

    with tab4:
        st.subheader("Métriques de comparaison")

        # Préparation des données pour le tableau
        metrics_data = []
        all_metrics_values = {
            "returns": [],
            "volatility": [],
            "sharpe": [],
            "sortino": [],
            "drawdown": [],
        }

        # Premier passage pour collecter toutes les valeurs
        for ticker in tickers:
            etf_data = df[df["ticker"] == ticker].copy()
            etf_data.set_index("date", inplace=True)
            returns = calculate_returns(etf_data["close"])

            # Calcul des métriques
            ann_return = returns.mean() * 252
            volatility = calculate_volatility(returns).iloc[-1]
            sharpe = calculate_sharpe_ratio(returns, risk_free_rate).iloc[-1]
            sortino = calculate_sortino_ratio(returns, risk_free_rate).iloc[-1]
            max_dd = calculate_max_drawdown(etf_data["close"])

            # Stockage des valeurs pour normalisation
            all_metrics_values["returns"].append(ann_return)
            all_metrics_values["volatility"].append(volatility)
            all_metrics_values["sharpe"].append(sharpe)
            all_metrics_values["sortino"].append(sortino)
            all_metrics_values["drawdown"].append(abs(max_dd))

            metrics_data.append(
                {
                    "ETF": f"{ticker} - {etf_names[ticker]}",
                    "Rendement annualisé": f"{ann_return:.2%}",
                    "Volatilité": f"{volatility:.2%}",
                    "Ratio de Sharpe": f"{sharpe:.2f}",
                    "Ratio de Sortino": f"{sortino:.2f}",
                    "Drawdown Max": f"{max_dd:.2%}",
                }
            )

        # Affichage du tableau des métriques
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df.set_index("ETF"), use_container_width=True)

        # Fonction de normalisation min-max
        def normalize_minmax(values):
            min_val = min(values)
            max_val = max(values)
            if min_val == max_val:
                return [1.0] * len(values)
            return [(x - min_val) / (max_val - min_val) for x in values]

        # Normalisation des métriques
        normalized_values = {
            "returns": normalize_minmax(all_metrics_values["returns"]),
            "volatility": normalize_minmax(
                [-x for x in all_metrics_values["volatility"]]
            ),  # Inversion car moins de volatilité est mieux
            "sharpe": normalize_minmax(all_metrics_values["sharpe"]),
            "sortino": normalize_minmax(all_metrics_values["sortino"]),
            "drawdown": normalize_minmax(
                [-x for x in all_metrics_values["drawdown"]]
            ),  # Inversion car moins de drawdown est mieux
        }

        # Graphique radar des métriques
        radar_metrics = [
            "Rendement annualisé",
            "Volatilité",
            "Ratio de Sharpe",
            "Ratio de Sortino",
            "Drawdown Max",
        ]

        radar_data = []
        for i, ticker in enumerate(tickers):
            values = [
                normalized_values["returns"][i],
                normalized_values["volatility"][i],
                normalized_values["sharpe"][i],
                normalized_values["sortino"][i],
                normalized_values["drawdown"][i],
            ]

            radar_data.append(
                go.Scatterpolar(
                    r=values,
                    theta=radar_metrics,
                    name=f"{ticker} - {etf_names[ticker]}",
                    fill="toself",
                )
            )

        radar_fig = go.Figure(data=radar_data)
        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    showticklabels=False,  # Cache les valeurs numériques
                    range=[0, 1],  # Force l'échelle de 0 à 1
                )
            ),
            showlegend=True,
            title="Comparaison des métriques (normalisées)",
        )
        st.plotly_chart(radar_fig)

        # Légende des métriques mise à jour
        st.caption(
            """
        - Rendement annualisé : performance moyenne sur un an
        - Volatilité : mesure de la variation des rendements (normalisée et inversée : plus c'est haut, moins il y a de volatilité)
        - Ratio de Sharpe : rendement ajusté du risque (> 1 est bon)
        - Ratio de Sortino : comme Sharpe mais ne pénalise que les pertes
        - Drawdown Max : perte maximale sur la période (normalisée et inversée : plus c'est haut, moins il y a de drawdown)
        - Si certaines métriques sont NaN, essayer de bouger la période et/ou le taux sans risque.
        - Toutes les métriques sont normalisées sur une échelle de 0 à 1, où 1 représente la meilleure performance relative.
        """
        )
