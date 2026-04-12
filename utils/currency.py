import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("EXCHANGE_API_KEY", "")

def get_rates(base_currency):
    if not API_KEY:
        return {}
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            return json.loads(data).get("conversion_rates", {})
    except Exception as e:
        print(f"Erreur taux de change : {e}")
        return {}

def convert(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    rates = get_rates(from_currency)
    if not rates:
        return amount
    rate = rates.get(to_currency)
    if rate is None:
        return amount
    return amount * rate