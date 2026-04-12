import urllib.request
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / "secrets.env")

API_KEY = os.getenv("EXCHANGE_API_KEY", "")

# Cache : { "EUR": {"rates": {...}, "timestamp": 1234567890} }
_cache = {}
CACHE_DURATION = 3600  # 1 heure en secondes

def get_rates(base_currency):
    if not API_KEY:
        print("ERREUR : clé API manquante dans secrets.env")
        return {}

    # Vérifier si le cache est encore valide
    if base_currency in _cache:
        age = time.time() - _cache[base_currency]["timestamp"]
        if age < CACHE_DURATION:
            return _cache[base_currency]["rates"]

    # Appel API uniquement si cache expiré ou absent
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = response.read()
            rates = json.loads(data).get("conversion_rates", {})
            # Stocker dans le cache
            _cache[base_currency] = {
                "rates":     rates,
                "timestamp": time.time(),
            }
            print(f"Taux mis en cache depuis {base_currency} : {len(rates)} devises")
            return rates
    except Exception as e:
        print(f"Erreur récupération taux : {e}")
        return {}

def convert(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    rates = get_rates(from_currency)
    if not rates:
        return amount
    rate = rates.get(to_currency)
    if rate is None:
        print(f"Taux introuvable pour {to_currency}")
        return amount
    return amount * rate