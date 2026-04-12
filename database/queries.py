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
    conn = get_connection()
    transactions = conn.execute("""
        SELECT transactions.*, categories.name, categories.color
        FROM transactions
        LEFT JOIN categories ON transactions.category_id = categories.id
        WHERE transactions.user_id = ? ORDER BY transactions.date DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    return [dict(r) for r in transactions]

def insert_transaction(user_id, amount, description, date, tx_type, category_id):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO transactions (user_id, amount, description, date, type, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, amount, description, date, tx_type, category_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur insert_transaction : {e}")
        return False
    
def get_categories_for_user(user_id):
    conn = get_connection()
    categories = conn.execute("""
        SELECT * FROM categories
        WHERE user_id = ?
        ORDER BY name ASC
    """, (user_id,)).fetchall()
    return [dict(r) for r in categories]

def insert_category(user_id, name, color):
    conn = get_connection()
    categorie = conn.execute("""
        SELECT * FROM categories WHERE user_id = ? AND LOWER(name) = LOWER(?)
    """, (user_id, name)).fetchone() #vérifie si une catégorie avec le même nom existe déjà pour l'utilisateur

    if categorie:
        return (False, "Une catégorie avec ce nom existe déjà.") #si une catégorie avec le même nom existe déjà, retourne False et un message d'erreur  
    
    conn.execute("""
        INSERT INTO categories (user_id, name, color)
        VALUES (?, ?, ?)
    """, (user_id, name, color)) #insère la nouvelle catégorie dans la base de données
    conn.commit() #valide les changements dans la base de données
    return (True, "Catégorie ajoutée avec succès.")

def delete_category(category_id, user_id):
    conn = get_connection()
    categorie = conn.execute("""
        SELECT * FROM categories WHERE id = ? AND user_id = ?
    """, (category_id, user_id)).fetchone() #récupère la catégorie à supprimer

    if not categorie:
        return (False, "Catégorie non trouvée.") #si la catégorie n'existe pas, retourne False et un message d'erreur

    conn.execute("""
        DELETE FROM categories WHERE id = ? AND user_id = ?
    """, (category_id, user_id)) #supprime la catégorie de la base de données
    conn.commit() #valide les changements dans la base de données
    return (True, "Catégorie supprimée.")

def seed_default_categories(user_id):
    conn = get_connection()
    default_categories = [
        ("Alimentation", "#1D9E75"),
        ("Abonnements", "#5DCAA5"),
        ("Courses", "#F09595"),
        ("Divers", "#F2B880"),
        ("Sorties", "#A66BFF"),
        ("Santé", "#FF6B6B"),
        ("Transport", "#4ECDC4"),
    ]
    for name, color in default_categories:
        existing = conn.execute("""
            SELECT * FROM categories WHERE user_id = ? AND name = ?
        """, (user_id, name)).fetchone()
        if not existing:
            conn.execute("""
                INSERT INTO categories (user_id, name, color)
                VALUES (?, ?, ?)
            """, (user_id, name, color))
    conn.commit()

def get_transactions(user_id, month=None, category_id=None, tx_type=None):
    conn = get_connection()
    query = """
        SELECT transactions.*, categories.name as category_name, categories.color as category_color
        FROM transactions
        LEFT JOIN categories ON transactions.category_id = categories.id
        WHERE transactions.user_id = ?
    """
    params = [user_id]

    if month:
        query += " AND strftime('%Y-%m', transactions.date) = ?"
        params.append(month)
    if category_id:
        query += " AND transactions.category_id = ?"
        params.append(category_id)
    if tx_type:
        query += " AND transactions.type = ?"
        params.append(tx_type)

    query += " ORDER BY transactions.date DESC"

    results = conn.execute(query, params).fetchall()
    return [dict(r) for r in results]

def update_transaction(tx_id, user_id, amount, description, date, tx_type, category_id):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE transactions
            SET amount = ?, description = ?, date = ?, type = ?, category_id = ?
            WHERE id = ? AND user_id = ?
        """, (amount, description, date, tx_type, category_id, tx_id, user_id)) #met à jour une transaction existante dans la base de données en fonction de son ID et de l'ID de l'utilisateur
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur update_transaction : {e}")
        return False
    
def delete_transaction(tx_id, user_id):
    conn = get_connection()
    try:
        conn.execute("""
            DELETE FROM transactions WHERE id = ? AND user_id = ?
        """, (tx_id, user_id)) #supprime une transaction de la base de données en fonction de son ID et de l'ID de l'utilisateur
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur delete_transaction : {e}")
        return False
    
def get_available_months(user_id):
    conn = get_connection()
    months = conn.execute("""
        SELECT DISTINCT strftime('%Y-%m', date) AS month
        FROM transactions
        WHERE user_id = ?
        ORDER BY month DESC
    """, (user_id,)).fetchall() #récupère les mois pour lesquels l'utilisateur a des transactions dans la base de données
    return [r["month"] for r in months]

def get_total_balance(user_id):
    """Solde cumulé depuis le début — toutes dates confondues."""
    conn = get_connection()
    revenus = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM transactions
        WHERE user_id = ? AND type = 'revenu'
    """, (user_id,)).fetchone()[0]
    depenses = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM transactions
        WHERE user_id = ? AND type = 'depense'
    """, (user_id,)).fetchone()[0]
    return revenus - depenses