import json

DEVISES = {
    "EUR": "€",
    "USD": "$",
    "FCFA": "FCFA",
    "GBP": "£",
}

DEFAULT_CONFIG = {
    "devise": "EUR",
    "symbole": "€",
    "devise_base": "EUR",
    "api_key": ""
}

def get_config():
    try:
        with open("config.json", "r") as f:
            fichier = json.load(f)
            return fichier if fichier else DEFAULT_CONFIG
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG

def save_config(data):
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)