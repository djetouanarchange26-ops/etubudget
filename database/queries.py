from database.connection import get_connection

def create_user(username, password_hash):

    conn = get_connection() #obtenir la connexion à la base de données
    existing_user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone() #exécuter une requête pour vérifier si un utilisateur avec le même nom d'utilisateur existe déjà dans la base de données
    if existing_user:
        return (False, "Le nom d'utilisateur existe déjà.") #si le nom d'utilisateur existe déjà, retourne False et un message d'erreur
    conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash)) #insérer le nouvel utilisateur dans la base de données
    conn.commit() #valider les changements dans la base de données
    return (True, "Utilisateur créé avec succès.") #retourne True et un message de succès
    

def get_user_by_username(username):
    conn = get_connection() #obtenir la connexion à la base de données
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone() #exécuter une requête pour récupérer l'utilisateur correspondant au nom d'utilisateur fourni
    if user is None: #si aucun utilisateur n'est trouvé, retourne None
        return None
    return dict(user) #si un utilisateur est trouvé, retourne un dictionnaire contenant les informations de l'utilisateur

def get_monthly_summary(user_id, month):
    conn = get_connection() #obtenir la connexion à la base de données
    nombre_transactions = conn.execute("""
        SELECT COUNT(*) AS total_transactions from transactions WHERE strftime('%Y-%m', date) = ? AND user_id = ?
    """, (month, user_id)).fetchone()[0] #exécuter une requête pour récupérer le résumé mensuel des transactions de l'utilisateur pour le mois spécifié

    total_revenu = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) from transactions WHERE type = "revenu" AND strftime('%Y-%m', date) = ? AND user_id = ? AND amount > 0
    """, (month, user_id)).fetchone()[0] #exécuter une requête pour récupérer le total des revenus de l'utilisateur pour le mois spécifié

    total_depense = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) from transactions WHERE type = "depense" AND strftime('%Y-%m', date) = ? AND user_id = ? AND amount > 0
    """, (month, user_id)).fetchone()[0] #exécuter une requête pour récupérer le total des dépenses de l'utilisateur pour le mois spécifié

    return {
    "nb_transactions": nombre_transactions,
    "total_revenus":   total_revenu,
    "total_depenses":  total_depense,
    "solde":           (total_revenu or 0) - (total_depense or 0)}

def get_last_transactions(user_id, limit=5):
    conn = get_connection() #obtenir la connexion à la base de données
    transactions = conn.execute("""
        SELECT * FROM transactions
        LEFT JOIN categories ON transactions.category_id = categories.id
        WHERE user_id = ? ORDER BY date DESC LIMIT ?
    """, (user_id, limit)).fetchall() #exécuter une requête pour récupérer les dernières transactions de l'utilisateur, triées par date décroissante et limitées au nombre spécifié
    return [dict(r) for r in transactions] #retourner une liste de dictionnaires contenant les informations des transactions récupérées