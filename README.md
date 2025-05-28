# Projet d'Analyse d'ETF

Ce projet permet d'analyser et de comparer des ETF en utilisant des données historiques de Yahoo Finance.

## Fonctionnalités

- Analyse individuelle d'ETF (prix, rendements, volatilité)
- Comparaison d'ETF par thème
- Visualisation interactive avec Streamlit
- Stockage des données historiques en local

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Récupérer les données :
```bash
python run_etl_script.py
```

2. Lancer l'application Streamlit :
```bash
streamlit run main.py
```

## Structure du Projet

- `config.yaml` : Configuration du projet
- `config_loader.py` : Chargement de la configuration
- `etl.py` : Extraction et transformation des données
- `helpers_analysis.py` : Fonctions d'analyse
- `main.py` : Point d'entrée de l'application Streamlit
- `repository.py` : Gestion de la base de données
- `view.py` : Interface utilisateur