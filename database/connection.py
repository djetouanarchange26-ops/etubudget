import sqlite3
import os
from pathlib import Path

_conn = None

def get_db_path() -> str:
    """Retourne le chemin vers la BDD dans les Documents de l'utilisateur."""
    # Dossier Documents de l'utilisateur
    docs = Path.home() / "Documents" / "EtuBudget"
    docs.mkdir(parents=True, exist_ok=True)
    return str(docs / "etubudget.db")

def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(get_db_path())
        _conn.row_factory = sqlite3.Row
    return _conn