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

def validate_transaction_fields(amount_str, date_str):
    """Valide et convertit les champs du formulaire de transaction."""
    # Montant
    if not amount_str or not amount_str.strip():
        return (False, "Le montant est obligatoire.", 0, "")
    try:
        amount = float(amount_str.strip().replace(",", "."))
        if amount <= 0:
            return (False, "Le montant doit être positif.", 0, "")
    except ValueError:
        return (False, "Montant invalide — utilise un point ou une virgule.", 0, "")

    # Date
    if not date_str or not date_str.strip():
        return (False, "La date est obligatoire.", 0, "")
    try:
        from datetime import datetime
        # Accepte JJ/MM/AAAA et YYYY-MM-DD
        date_str = date_str.strip()
        if "/" in date_str:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        date_iso = date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return (False, "Format de date invalide — utilise JJ/MM/AAAA.", 0, "")

    return (True, "", amount, date_iso)