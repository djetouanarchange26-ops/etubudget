import hashlib

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, stored_hash):
    """Check if the provided password matches the stored hash."""
    return hash_password(password) == stored_hash

def validate_login_fields(username, password):
    nom_utilisateur = username.strip() #supprime les espaces avant et après le nom d'utilisateur
    mot_de_passe = password.strip() #supprime les espaces avant et après le mot de passe
    
    """S'assure que les champs de connexion ne sont pas vides."""
    if not nom_utilisateur or not mot_de_passe:
        return (False, "Veuillez remplir tous les champs de connexion.")

    """S'assure que le nom d'utilisateur et le mot de passe respectent les critères de longueur."""
    if len(nom_utilisateur) < 3: #vérifie que le nom d'utilisateur contient au moins 3 caractères
        return (False, "Le nom d'utilisateur doit contenir au moins 3 caractères.")
    if len(mot_de_passe) < 6: #vérifie que le mot de passe contient au moins 6 caractères
        return (False, "Le mot de passe doit contenir au moins 6 caractères.")
    
    return (True, "") #si les champs sont valides, retourne True et un message vide