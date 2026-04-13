import customtkinter as ctk
from utils.config import is_seen, mark_seen


MESSAGES = {
    "dashboard": {
        "titre":   "Bienvenue sur ton dashboard",
        "texte":   "Ici tu retrouves ton solde cumulé depuis le début, "
                   "le résumé du mois sélectionné et tes dernières transactions.\n\n"
                   "Change le mois en haut pour explorer ton historique.",
        "emoji":   "👋",
    },
    "ajouter": {
        "titre":   "Ajouter une transaction",
        "texte":   "Saisis ici tes dépenses et revenus.\n\n"
                   "Le montant doit être positif — c'est le type (dépense/revenu) "
                   "qui indique le sens.\n"
                   "La description est optionnelle, mais une catégorie "
                   "te donnera de meilleures statistiques.",
        "emoji":   "💸",
    },
    "categories": {
        "titre":   "Gérer tes catégories",
        "texte":   "Crée des catégories personnalisées avec des couleurs.\n\n"
                   "Elles apparaissent dans tes statistiques et dans le "
                   "formulaire d'ajout.\n"
                   "Supprimer une catégorie ne supprime pas les transactions liées.",
        "emoji":   "🏷️",
    },
    "historique": {
        "titre":   "Historique de tes transactions",
        "texte":   "Retrouve toutes tes transactions ici.\n\n"
                   "Utilise les filtres (mois, catégorie, type) pour analyser "
                   "une période précise.\n"
                   "Tu peux modifier ou supprimer une transaction en cliquant dessus.",
        "emoji":   "📋",
    },
    "stats": {
        "titre":   "Tes statistiques",
        "texte":   "Visualise tes habitudes financières.\n\n"
                   "La courbe montre tes dépenses jour par jour.\n"
                   "Le camembert répartit tes dépenses par catégorie.\n"
                   "Change le mois en haut pour explorer ton historique.",
        "emoji":   "📊",
    },
    "exporter": {
        "titre":   "Exporter tes données",
        "texte":   "Télécharge ton historique en CSV (compatible Excel) "
                   "ou en PDF (relevé mis en page).\n\n"
                   "Tu peux choisir d'exporter toutes tes transactions "
                   "ou uniquement un mois précis.",
        "emoji":   "📤",
    },
}


class OnboardingOverlay(ctk.CTkToplevel):
    def __init__(self, parent, feature_name: str):
        super().__init__(parent)

        msg = MESSAGES.get(feature_name)
        if not msg:
            self.destroy()
            return

        # ── Fenêtre ───────────────────────────────────────────
        self.title("")
        self.geometry("420x320")
        self.resizable(False, False)
        self.grab_set()
        mark_seen(feature_name)

        # Centrer par rapport au parent
        self.after(10, self._center)

        # Fond
        self.configure(fg_color="#16213e")

        # ── Contenu ───────────────────────────────────────────
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=28, pady=24)

        # Emoji + titre
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            header,
            text=msg["emoji"],
            font=ctk.CTkFont(size=36),
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            header,
            text=msg["titre"],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e8e8f0",
            wraplength=300,
            justify="left",
        ).pack(side="left", anchor="w")

        # Séparateur
        ctk.CTkFrame(
            content, height=1, fg_color="#2a2a4a"
        ).pack(fill="x", pady=(0, 16))

        # Texte explicatif
        ctk.CTkLabel(
            content,
            text=msg["texte"],
            font=ctk.CTkFont(size=12),
            text_color="#9090a8",
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(0, 20))

        # Boutons
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row,
            text="J'ai compris !",
            height=38,
            fg_color="#1D9E75",
            hover_color="#0F6E56",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._close,
        ).pack(side="right")

        ctk.CTkButton(
            btn_row,
            text="Ne plus afficher",
            height=38,
            fg_color="transparent",
            border_width=1,
            border_color="#3a3a5a",
            text_color="#9090a8",
            hover_color="#1a1a2e",
            font=ctk.CTkFont(size=12),
            command=lambda: self._close(permanent=True),
        ).pack(side="right", padx=(0, 8))

        self.feature_name = feature_name

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_width()
        ph = self.master.winfo_height()
        px = self.master.winfo_x()
        py = self.master.winfo_y()
        w  = self.winfo_width()
        h  = self.winfo_height()
        x  = px + (pw - w) // 2
        y  = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _close(self, permanent=False):
        if permanent:
            mark_seen(self.feature_name)
        self.grab_release()
        self.destroy()


def show_onboarding(parent, feature_name: str):
    if not is_seen(feature_name):
        parent.after(500, lambda: OnboardingOverlay(parent, feature_name))