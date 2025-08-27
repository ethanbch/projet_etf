# Projet d'Analyse d'ETF

Application d'analyse et de comparaison d'ETF utilisant des données historiques de Yahoo Finance, avec visualisation interactive via Streamlit.

## Lien Github

https://github.com/ethanbch/projet_etf/tree/master

## Installation

1. Cloner le dépôt :

```bash
git clone https://github.com/ethanbch/projet_etf.git
cd projet_etf # ou en tout cas le chemin où vous avez mis le dossier
```

2. Créer et activer un environnement virtuel :

```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
.\venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Utilisation

1. Récupérer les données historiques :

```bash
python run_etl_script.py
```

2. Lancer l'application Streamlit :

```bash
streamlit run main.py
```

3. Accéder à l'interface via votre navigateur

## Fonctionnalités

### Analyse Individuelle

- Suivi des prix et volumes
- Calcul des rendements (journaliers et cumulés)
- Métriques de risque :
  - Volatilité annualisée
  - Ratio de Sharpe
  - Ratio de Sortino
  - Drawdown maximum

### Comparaison d'ETF

- Performance relative (base 100)
- Analyse risque/rendement
- Matrice de corrélation
- Tableau comparatif des métriques
- Visualisation radar des performances

### Données et Configuration

- ETL automatisé depuis Yahoo Finance
- Stockage local SQLite
- Configuration YAML flexible pour ajouter/modifier les ETF suivis

## Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Un terminal pour exécuter les commandes

## Architecture du Projet

config.yaml : Configuration des ETF et paramètres  
config_loader.py : Gestion de la configuration  
etl.py : Pipeline d'extraction des données  
helpers_analysis.py : Fonctions d'analyse financière  
main.py : Point d'entrée de l'application  
repository.py : Couche d'accès aux données  
view.py : Interface utilisateur Streamlit  
requirements.txt : Dépendances Python

## 🛠️ Stack Technique

- **Données**: Yahoo Finance (via yfinance)
- **Base de données**: SQLite
- **Interface**: Streamlit
- **Visualisation**: Plotly
- **Analyse**: Pandas, NumPy
- **Configuration**: YAML

## 📝 Notes Techniques

- La base de données est créée automatiquement dans le dossier `data/`
- Architecture en deux tables avec jointure :
  - `etf_metadata` : Informations descriptives des ETF (ticker, nom, thème)
  - `etf_prices` : Données historiques de prix
  - Jointure automatique lors de la récupération des données via le repository
- Les données sont mises à jour à chaque exécution de l'ETL
- Le taux sans risque est configurable dans l'interface
- Périodes d'analyse disponibles : 1m, 3m, 6m, YTD, 1a, 3a, 5a, MAX
