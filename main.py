"""
Point d'entrée principal de l'application Streamlit.
"""

import pandas as pd
import streamlit as st

from config_loader import load_config
from helpers_analysis import get_date_range
from repository import EtfRepository
from view import display_etf_analysis, display_etf_comparison


def create_etf_labels(config):
    """Crée un dictionnaire de labels pour les ETF."""
    return {etf["ticker"]: f"{etf['ticker']} - {etf['name']}" for etf in config["etfs"]}


def main():
    st.title("Analyse d'ETF")

    # Chargement de la configuration et initialisation
    config = load_config()
    repository = EtfRepository(config)

    # Création des labels pour les ETF
    etf_labels = create_etf_labels(config)
    tickers = list(etf_labels.keys())

    # Sidebar pour la navigation
    page = st.sidebar.radio(
        "Navigation", ["Analyse individuelle", "Comparaison d'ETFs"]
    )

    # Paramètres d'analyse
    st.sidebar.subheader("Paramètres d'analyse")

    # Sélection de la période
    periods = ["1m", "3m", "6m", "YTD", "1a", "5a", "MAX"]
    selected_period = st.sidebar.select_slider(
        "Période", options=periods, value="1a"  # Valeur par défaut : 1 an
    )

    # Sélection du taux sans risque
    risk_free_rate = (
        st.sidebar.slider(
            "Taux sans risque (%)",
            min_value=0.0,
            max_value=5.0,
            value=2.0,
            step=0.1,
            help="Taux utilisé pour le calcul du ratio de Sharpe",
        )
        / 100
    )  # Conversion en décimal

    # Calcul des dates en fonction de la période
    start_date, end_date = get_date_range(selected_period)

    if page == "Analyse individuelle":
        # Sélection de l'ETF avec nom complet
        selected_label = st.sidebar.selectbox(
            "Sélectionner un ETF", options=[etf_labels[ticker] for ticker in tickers]
        )
        selected_ticker = selected_label.split(" - ")[0]  # Récupère le ticker

        # Récupération et affichage des données
        etf_data = repository.get_etf_data(
            selected_ticker,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
        )
        if not etf_data.empty:
            display_etf_analysis(etf_data, selected_label, risk_free_rate)
        else:
            st.error("Aucune donnée disponible pour cet ETF.")

    else:  # Comparaison d'ETFs
        # Sélection multiple d'ETFs avec noms complets
        selected_labels = st.sidebar.multiselect(
            "Sélectionner les ETFs à comparer",
            options=[etf_labels[ticker] for ticker in tickers],
            default=[
                etf_labels[tickers[0]],
                etf_labels[tickers[1]],
            ],  # Les 2 premiers par défaut
        )
        selected_tickers = [
            label.split(" - ")[0] for label in selected_labels
        ]  # Récupère les tickers

        if len(selected_tickers) < 2:
            st.warning("Veuillez sélectionner au moins 2 ETFs pour la comparaison.")
        else:
            # Récupération des données pour tous les ETFs sélectionnés
            comparison_data = pd.DataFrame()
            for ticker in selected_tickers:
                data = repository.get_etf_data(
                    ticker,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                )
                if not data.empty:
                    comparison_data = pd.concat([comparison_data, data])

            if not comparison_data.empty:
                display_etf_comparison(
                    comparison_data, selected_tickers, risk_free_rate
                )
            else:
                st.error("Aucune donnée disponible pour les ETFs sélectionnés.")


if __name__ == "__main__":
    main()
