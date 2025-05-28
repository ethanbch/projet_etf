"""
Point d'entrée principal de l'application Streamlit.
"""

import streamlit as st
from config_loader import load_config
from repository import EtfRepository
from view import display_etf_analysis, display_etf_comparison


def main():
    st.title("Analyse d'ETF")
    
    # Chargement de la configuration et initialisation
    config = load_config()
    repository = EtfRepository(config)
    
    # Sidebar pour la navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Analyse individuelle", "Comparaison thématique"]
    )
    
    if page == "Analyse individuelle":
        # Sélection de l'ETF
        tickers = [etf['ticker'] for etf in config['etfs']]
        selected_ticker = st.sidebar.selectbox(
            "Sélectionner un ETF",
            tickers
        )
        
        # Récupération et affichage des données
        etf_data = repository.get_etf_data(selected_ticker)
        if not etf_data.empty:
            display_etf_analysis(etf_data, selected_ticker)
        else:
            st.error("Aucune donnée disponible pour cet ETF.")
    
    else:  # Comparaison thématique
        # Sélection du thème
        themes = repository.get_all_themes()
        selected_theme = st.sidebar.selectbox(
            "Sélectionner un thème",
            themes
        )
        
        # Récupération et affichage des données
        theme_data = repository.get_etf_by_theme(selected_theme)
        if not theme_data.empty:
            tickers = theme_data['ticker'].unique().tolist()
            display_etf_comparison(theme_data, tickers)
        else:
            st.error("Aucune donnée disponible pour ce thème.")


if __name__ == "__main__":
    main()