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