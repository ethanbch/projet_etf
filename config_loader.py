"""
Module de chargement de la configuration depuis le fichier YAML.
Définit les types et structures de données pour la configuration du projet ETF.
"""

from pathlib import Path
from typing import Dict, List, TypedDict

import yaml


class EtfConfig(TypedDict):
    """Structure des données de configuration pour un ETF individuel.

    :param ticker: Code de l'ETF sur le marché
    :param name: Nom complet de l'ETF
    :param theme: Thème ou catégorie de l'ETF
    """

    ticker: str
    name: str
    theme: str


class Config(TypedDict):
    """Structure globale de la configuration du projet.

    :param database: Configuration de la base de données
    :param date_range: Plage de dates pour l'extraction des données
    :param etfs: Liste des ETF à suivre
    """

    database: Dict[str, str]
    date_range: Dict[str, str]
    etfs: List[EtfConfig]


def load_config() -> Config:
    """Charge la configuration depuis le fichier config.yaml.

    :return: Configuration complète du projet
    :rtype: Config
    :raises FileNotFoundError: Si config.yaml n'existe pas
    """
    config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError("Le fichier config.yaml n'a pas été trouvé")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)
