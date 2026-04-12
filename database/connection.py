import sqlite3

_conn = None #variable globale initialisée à None qui contiendra la connexion à la base de données

def get_connection():
    global _conn #indique que nous allons utiliser la variable globale _conn

    if _conn is None: #si la connexion n'a pas encore été établie
        _conn = sqlite3.connect('etubudget.db') #établit une connexion à la base de données et l'assigne à la variable globale _conn
        _conn.row_factory = sqlite3.Row #permet de récupérer les résultats des requêtes sous forme de dictionnaires
    return _conn #retourne la connexion à la base de données