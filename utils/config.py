import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / "secrets.env")

DEVISES = {
    "EUR": "€",
    "USD": "$",
    "XOF": "FCFA",
    "GBP": "£",
}

def _default():
    return {
        "devise":      "EUR",
        "symbole":     "€",
        "devise_base": "EUR",
        "api_key":     os.getenv("EXCHANGE_API_KEY", ""),
    }

def get_config():
    try:
        with open("config.json", "r") as f:
            fichier = json.load(f)
            if not fichier:
                return _default()
            # Toujours injecter la clé API depuis secrets.env
            fichier["api_key"] = os.getenv("EXCHANGE_API_KEY", "")
            # S'assurer que devise_base est présent
            if "devise_base" not in fichier:
                fichier["devise_base"] = "EUR"
            return fichier
    except (FileNotFoundError, json.JSONDecodeError):
        return _default()

def save_config(data):
    # Ne jamais sauvegarder la clé API dans config.json
    data_to_save = {k: v for k, v in data.items() if k != "api_key"}
    with open("config.json", "w") as f:
        json.dump(data_to_save, f, indent=4)