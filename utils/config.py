import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger la clé API depuis secrets.env
# Fonctionne en dev (fichier local) et en prod (PyInstaller embed)
if getattr(sys, 'frozen', False):
    # Mode PyInstaller — secrets.env est dans le dossier temporaire
    base_path = Path(sys._MEIPASS)
else:
    # Mode dev — secrets.env est à la racine du projet
    base_path = Path(__file__).parent.parent

load_dotenv(dotenv_path=base_path / "secrets.env")

DEVISES = {
    "EUR": "€",
    "USD": "$",
    "XOF": "FCFA",
    "GBP": "£",
    "MAD": "DH"
}


def _get_app_dir() -> Path:
    """Retourne le dossier Documents/EtuBudget — créé si nécessaire."""
    app_dir = Path.home() / "Documents" / "EtuBudget"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def _get_config_path() -> Path:
    return _get_app_dir() / "config.json"


def _default() -> dict:
    return {
        "devise":      "EUR",
        "symbole":     "€",
        "devise_base": "EUR",
        "api_key":     os.getenv("EXCHANGE_API_KEY", ""),
        "theme":       "dark",
        "onboarding_seen": {
            "dashboard":  False,
            "ajouter":    False,
            "categories": False,
            "historique": False,
            "stats":      False,
            "exporter":   False,
        },
    }


def get_config() -> dict:
    try:
        with open(_get_config_path(), "r") as f:
            fichier = json.load(f)
            if not fichier:
                return _default()
            # Toujours injecter la clé API depuis secrets.env
            fichier["api_key"] = os.getenv("EXCHANGE_API_KEY", "")
            # S'assurer que les clés obligatoires sont présentes
            if "devise_base" not in fichier:
                fichier["devise_base"] = "EUR"
            if "onboarding_seen" not in fichier:
                fichier["onboarding_seen"] = _default()["onboarding_seen"]
            if "theme" not in fichier:
                fichier["theme"] = "dark"
            return fichier
    except (FileNotFoundError, json.JSONDecodeError):
        return _default()


def save_config(data: dict) -> None:
    """Sauvegarde le config — sans jamais écrire la clé API sur le disque."""
    data_to_save = {k: v for k, v in data.items() if k != "api_key"}
    with open(_get_config_path(), "w") as f:
        json.dump(data_to_save, f, indent=4)


def mark_seen(feature_name: str) -> None:
    config = get_config()
    if "onboarding_seen" not in config:
        config["onboarding_seen"] = {}
    config["onboarding_seen"][feature_name] = True
    save_config(config)


def is_seen(feature_name: str) -> bool:
    config = get_config()
    return config.get("onboarding_seen", {}).get(feature_name, False)