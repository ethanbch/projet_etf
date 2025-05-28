"""
Module de chargement de la configuration pour l'application d'analyse d'ETF.
"""

import yaml
from typing import Dict, List, TypedDict
from pathlib import Path


class EtfConfig(TypedDict):
    ticker: str
    name: str
    theme: str


class Config(TypedDict):
    database: Dict[str, str]
    date_range: Dict[str, str]
    etfs: List[EtfConfig]


def load_config() -> Config:
    """Charge la configuration depuis le fichier YAML."""
    config_path = Path(__file__).parent / 'config.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError("Le fichier config.yaml n'a pas été trouvé")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)