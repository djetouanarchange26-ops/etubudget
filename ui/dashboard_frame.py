import customtkinter as ctk
from datetime import datetime
import state
from database.queries import get_monthly_summary, get_last_transactions
from utils.config import get_config


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current_month = datetime.now().strftime("%Y-%m")
        self._build()

    def _build(self):
        self.pack_propagate(True)
        self.columnconfigure(0, weight=1)

        # ── En-tête ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        header.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=f"Bonjour {state.current_username} 👋",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Voici ton résumé du mois",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).grid(row=1, column=0, sticky="w")

        # ── Cards ─────────────────────────────────────────────
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew",
                              padx=24, pady=(16, 0))
        for i in range(4):
            self.cards_frame.columnconfigure(i, weight=1)

        self._build_cards()

        # ── Dernières transactions ─────────────────────────────
        tx_header = ctk.CTkFrame(self, fg_color="transparent")
        tx_header.grid(row=2, column=0, sticky="ew", padx=24, pady=(20, 4))
        tx_header.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tx_header,
            text="Dernières transactions",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.tx_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=200
        )
        self.tx_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 16))
        self.tx_frame.columnconfigure(0, weight=1)

        self._build_transactions()

    def _build_cards(self):

        config = get_config()
        symbole = config.get("symbole", "€")

        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        summary = get_monthly_summary(state.current_user_id, self.current_month)

        cards_data = [
            ("Solde du mois",
            f"{summary['solde']:+.2f} {symbole}",
            "#5DCAA5" if summary["solde"] >= 0 else "#F09595"),
            ("Dépenses",
            f"{summary['total_depenses']:.2f} {symbole}",
            "#F09595"),
            ("Revenus",
            f"{summary['total_revenus']:.2f} {symbole}",
            "#5DCAA5"),
            ("Transactions",
            str(summary["nb_transactions"]),
            "#AFA9EC"),
        ]

        for i, (label, value, color) in enumerate(cards_data):
            card = ctk.CTkFrame(
                self.cards_frame,
                fg_color="#16213e",
                corner_radius=10,
            )
            card.grid(row=0, column=i, padx=(0, 10) if i < 3 else (0, 0),
                      sticky="ew")
            card.columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card, text=label,
                font=ctk.CTkFont(size=11),
                text_color="gray",
            ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))

            ctk.CTkLabel(
                card, text=value,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color,
            ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 12))

    def _build_transactions(self):
        # Vider la liste existante
        for widget in self.tx_frame.winfo_children():
            widget.destroy()

        transactions = get_last_transactions(state.current_user_id, limit=5)

        if not transactions:
            ctk.CTkLabel(
                self.tx_frame,
                text="Aucune transaction pour l'instant — commence à en ajouter !",
                text_color="gray",
                font=ctk.CTkFont(size=12),
            ).grid(row=0, column=0, pady=20)
            return

        for i, tx in enumerate(transactions):
            row = ctk.CTkFrame(
                self.tx_frame,
                fg_color="#16213e" if i % 2 == 0 else "transparent",
                corner_radius=8,
            )
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.columnconfigure(1, weight=1)

            # Pastille couleur catégorie
            color = tx.get("color") or "#5F5E5A"
            ctk.CTkLabel(
                row, text="",
                width=28, height=28,
                fg_color=color,
                corner_radius=6,
            ).grid(row=0, column=0, padx=(10, 8), pady=8, rowspan=2)

            # Nom + catégorie
            ctk.CTkLabel(
                row,
                text=tx.get("description") or "Sans description",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
            ).grid(row=0, column=1, sticky="w", pady=(8, 0))

            ctk.CTkLabel(
                row,
                text=tx.get("name") or "Sans catégorie",
                font=ctk.CTkFont(size=10),
                text_color="gray",
                anchor="w",
            ).grid(row=1, column=1, sticky="w", pady=(0, 8))

            # Date
            ctk.CTkLabel(
                row,
                text=tx.get("date", ""),
                font=ctk.CTkFont(size=10),
                text_color="gray",
            ).grid(row=0, column=2, padx=10, pady=(8, 0))

            # Montant
            symbole = get_config().get("symbole", "€")
            is_depense = tx.get("type") == "depense"
            montant_text = f"-{tx['amount']:.2f} {symbole}" if is_depense else f"+{tx['amount']:.2f} {symbole}"
            montant_color = "#F09595" if is_depense else "#5DCAA5"

            ctk.CTkLabel(
                row,
                text=montant_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=montant_color,
            ).grid(row=0, column=3, padx=(0, 14), pady=(8, 0))

    def refresh(self):
        self._build_cards()
        self._build_transactions()