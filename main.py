"""
Point d'entrée principal de l'application Streamlit.
"""

import pandas as pd
import streamlit as st

from config_loader import load_config
from helpers_analysis import get_date_range
from repository import EtfRepository
from view import display_etf_analysis, display_etf_comparison


def main():
    st.title("Analyse d'ETF")

    # Chargement de la configuration et initialisation
    config = load_config()
    repository = EtfRepository(config)

    # Sidebar pour la navigation
    page = st.sidebar.radio(
        "Navigation", ["Analyse individuelle", "Comparaison d'ETFs"]
    )

    # Sélection de la période
    periods = ["1m", "3m", "6m", "YTD", "1a", "5a", "MAX"]
    selected_period = st.sidebar.select_slider(
        "Période", options=periods, value="1a"  # Valeur par défaut : 1 an
    )

    # Calcul des dates en fonction de la période
    start_date, end_date = get_date_range(selected_period)

    if page == "Analyse individuelle":
        # Sélection de l'ETF
        tickers = [etf["ticker"] for etf in config["etfs"]]
        selected_ticker = st.sidebar.selectbox("Sélectionner un ETF", tickers)

        # Récupération et affichage des données
        etf_data = repository.get_etf_data(
            selected_ticker,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
        )
        if not etf_data.empty:
            display_etf_analysis(etf_data, selected_ticker)
        else:
            st.error("Aucune donnée disponible pour cet ETF.")

    else:  # Comparaison d'ETFs
        # Sélection multiple d'ETFs
        tickers = [etf["ticker"] for etf in config["etfs"]]
        selected_tickers = st.sidebar.multiselect(
            "Sélectionner les ETFs à comparer",
            tickers,
            default=tickers[:2],  # Sélectionne les 2 premiers par défaut
        )

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
                display_etf_comparison(comparison_data, selected_tickers)
            else:
                st.error("Aucune donnée disponible pour les ETFs sélectionnés.")


if __name__ == "__main__":
    main()
