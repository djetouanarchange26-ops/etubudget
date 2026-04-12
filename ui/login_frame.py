import customtkinter as ctk
import state
from utils.validators import hash_password, check_password, validate_login_fields
from database.queries import create_user, get_user_by_username


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        # Centrage horizontal
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)

        # ── Logo ──────────────────────────────────────────────
        logo = ctk.CTkLabel(
            self, text="E",
            width=56, height=56,
            fg_color="#1D9E75",
            corner_radius=14,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white",
        )
        logo.grid(row=0, column=1, pady=(60, 0))

        # ── Titre ─────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="EtuBudget",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=1, column=1, pady=(10, 2))

        ctk.CTkLabel(
            self, text="Tracker de dépenses étudiant",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).grid(row=2, column=1, pady=(0, 24))

        # ── Champ username ────────────────────────────────────
        self.entry_username = ctk.CTkEntry(
            self, placeholder_text="Nom d'utilisateur",
            width=300, height=40,
        )
        self.entry_username.grid(row=3, column=1, pady=(0, 10))
        self.entry_username.bind("<Return>", lambda e: self._login())

        # ── Champ password ────────────────────────────────────
        self.entry_password = ctk.CTkEntry(
            self, placeholder_text="Mot de passe",
            width=300, height=40,
            show="*",
        )
        self.entry_password.grid(row=4, column=1, pady=(0, 6))
        self.entry_password.bind("<Return>", lambda e: self._login())

        # ── Label erreur ──────────────────────────────────────
        self.label_error = ctk.CTkLabel(
            self, text="",
            text_color="#E24B4A",
            font=ctk.CTkFont(size=12),
        )
        self.label_error.grid(row=5, column=1, pady=(0, 14))

        # ── Bouton connexion ──────────────────────────────────
        ctk.CTkButton(
            self, text="Se connecter",
            width=300, height=40,
            fg_color="#1D9E75",
            hover_color="#0F6E56",
            command=self._login,
        ).grid(row=6, column=1, pady=(0, 8))

        # ── Bouton inscription ────────────────────────────────
        ctk.CTkButton(
            self, text="Créer un compte",
            width=300, height=40,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            hover_color=("gray85", "gray25"),
            command=self._signup,
        ).grid(row=7, column=1)

    # ── Logique connexion ──────────────────────────────────────
    def _login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # 1. Validation des champs
        ok, msg = validate_login_fields(username, password)
        if not ok:
            self.label_error.configure(text=msg)
            return

        # 2. Vérification que l'utilisateur existe
        user = get_user_by_username(username)
        if user is None:
            self.label_error.configure(text="Utilisateur introuvable.")
            return

        # 3. Vérification du mot de passe
        if not check_password(password, user["password_hash"]):
            self.label_error.configure(text="Mot de passe incorrect.")
            return

        # 4. Connexion réussie
        self.label_error.configure(text="")
        state.set_user(user["id"], user["username"])
        self.app.show_frame("accueil")

    # ── Logique inscription ────────────────────────────────────
    def _signup(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # 1. Validation des champs
        ok, msg = validate_login_fields(username, password)
        if not ok:
            self.label_error.configure(text=msg)
            return

        # 2. Création de l'utilisateur
        ok, msg = create_user(username, hash_password(password))
        if not ok:
            self.label_error.configure(text=msg)
            return

        # 3. Récupérer l'id du nouvel utilisateur
        user = get_user_by_username(username)

        # 4. Catégories par défaut (sera codé en S6)
        # seed_default_categories(user["id"])

        # 5. Connexion automatique après inscription
        state.set_user(user["id"], user["username"])
        self.label_error.configure(text="")
        self.app.show_frame("accueil")