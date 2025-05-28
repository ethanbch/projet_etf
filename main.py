import pandas as pd  # Assure-toi que c'est importé
import streamlit as st

from config_loader import load_config  # Nécessaire pour initialiser EtfRepository
from helpers_analysis import get_date_range
from repository import EtfRepository
from view import display_etf_analysis, display_etf_comparison


def main():
    st.set_page_config(layout="wide", page_title="Analyse d'ETF")
    st.title("📊 Analyse d'ETF")

    try:
        config = load_config()
    except FileNotFoundError as e:
        st.error(
            f"Erreur de configuration : {e}. Veuillez vous assurer que 'config.yaml' existe."
        )
        return  # Arrêter si la config n'est pas trouvée

    repository = EtfRepository(config)  # Passe la config chargée

    # --- Récupération des informations des ETF pour les sélecteurs ---
    etf_info_df = repository.get_all_etf_info_for_selection()

    if etf_info_df.empty:
        st.error(
            "Aucune métadonnée d'ETF trouvée dans la base. "
            "Veuillez exécuter le script ETL (`run_etl_script.py`) avant de lancer l'application."
        )
        return  # Arrêter l'exécution si pas de métadonnées

    # Création des labels pour les ETF à partir des données du repository
    # Format: "TICKER - Nom Complet de l'ETF"
    etf_labels_map = {  # Renommé pour plus de clarté (map de ticker vers label)
        row["ticker"]: f"{row['ticker']} - {row['name']}"
        for _, row in etf_info_df.iterrows()
    }
    # Liste des labels formatés pour les widgets Streamlit
    display_labels_options = list(etf_labels_map.values())

    # Mapping inverse pour retrouver le ticker à partir du label sélectionné
    ticker_from_label_map = {v: k for k, v in etf_labels_map.items()}

    # --- Sidebar pour la navigation et les paramètres ---
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Choisir une page :",
            ["Analyse individuelle", "Comparaison d'ETFs"],
            label_visibility="collapsed",
        )

        st.divider()
        st.header("Paramètres d'Analyse")

        # Sélection de la période
        periods = ["1m", "3m", "6m", "YTD", "1a", "3a", "5a", "MAX"]
        selected_period_label = st.select_slider(  # Renommé pour clarté
            "Période", options=periods, value="1a"  # Valeur par défaut : 1 an
        )

        # Sélection du taux sans risque
        risk_free_rate_percentage = st.slider(  # Renommé pour clarté
            "Taux sans risque (%)",
            min_value=0.0,
            max_value=5.0,
            value=2.0,  # Taux par défaut en pourcentage
            step=0.1,
            help="Taux annuel utilisé pour le calcul des ratios de Sharpe et Sortino.",
        )
        risk_free_rate_decimal = risk_free_rate_percentage / 100
    start_date_dt, end_date_dt = get_date_range(selected_period_label)
    start_date_str = start_date_dt.strftime("%Y-%m-%d")
    end_date_str = end_date_dt.strftime("%Y-%m-%d")

    st.caption(
        f"Période d'analyse sélectionnée : du {start_date_str} au {end_date_str} (Taux sans risque : {risk_free_rate_percentage:.1f}%)"
    )

    # Logique d'affichage des pages
    if page == "Analyse individuelle":
        if not display_labels_options:
            st.warning("Aucun ETF disponible pour la sélection.")
        else:
            selected_display_label = st.sidebar.selectbox(
                "Sélectionner un ETF", options=display_labels_options
            )
            if selected_display_label:  # S'assurer qu'une sélection a été faite
                selected_ticker = ticker_from_label_map[selected_display_label]

                # Récupération et affichage des données
                # repository.get_etf_data attend des strings pour les dates
                etf_data_for_analysis = repository.get_etf_data(
                    selected_ticker,
                    start_date_str,
                    end_date_str,
                )
                if not etf_data_for_analysis.empty:
                    # display_etf_analysis attend le label complet pour l'affichage du titre
                    display_etf_analysis(
                        etf_data_for_analysis,
                        selected_display_label,
                        risk_free_rate_decimal,
                    )
                else:
                    st.error(
                        f"Aucune donnée disponible pour {selected_display_label} sur la période sélectionnée."
                    )
            else:
                st.info("Veuillez sélectionner un ETF.")

    elif page == "Comparaison d'ETFs":
        if not display_labels_options or len(display_labels_options) < 2:
            st.warning(
                "Pas assez d'ETFs disponibles pour la comparaison (minimum 2 requis)."
            )
        else:
            # Sélection multiple d'ETFs avec noms complets
            # Définir des valeurs par défaut pour le multiselect
            default_multiselect_labels = []
            if len(display_labels_options) >= 1:
                default_multiselect_labels.append(display_labels_options[0])
            if len(display_labels_options) >= 2:
                default_multiselect_labels.append(display_labels_options[1])

            selected_display_labels_multi = (
                st.sidebar.multiselect(  # Renommé pour clarté
                    "Sélectionner les ETFs à comparer",
                    options=display_labels_options,
                    default=default_multiselect_labels,
                )
            )

            if not selected_display_labels_multi:
                st.info("Veuillez sélectionner au moins un ETF pour la comparaison.")
            elif len(selected_display_labels_multi) < 2:
                st.warning(
                    "Veuillez sélectionner au moins 2 ETFs pour une comparaison pertinente."
                )
            else:
                selected_tickers_multi = [
                    ticker_from_label_map[label]
                    for label in selected_display_labels_multi
                ]

                # Récupération des données pour tous les ETFs sélectionnés
                comparison_data_list = []  # Pour stocker les DataFrames de chaque ETF
                for ticker in selected_tickers_multi:
                    data = repository.get_etf_data(
                        ticker,
                        start_date_str,
                        end_date_str,
                    )
                    if not data.empty:
                        comparison_data_list.append(data)

                if comparison_data_list:
                    # Concaténer tous les DataFrames obtenus
                    all_comparison_data_df = pd.concat(
                        comparison_data_list, ignore_index=True
                    )
                    if not all_comparison_data_df.empty:
                        display_etf_comparison(
                            all_comparison_data_df,
                            selected_tickers_multi,
                            risk_free_rate_decimal,
                        )
                    else:
                        st.error(
                            "Les données concaténées pour la comparaison sont vides."
                        )
                else:
                    st.error(
                        "Aucune donnée disponible pour les ETFs sélectionnés sur la période."
                    )


if __name__ == "__main__":
    main()
