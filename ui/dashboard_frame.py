import customtkinter as ctk
from datetime import datetime
import state
from utils.config import get_config
from utils.currency import convert
from database.queries import (
    get_monthly_summary,
    get_last_transactions,
    get_available_months,
    get_total_balance,
)


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current_month = datetime.now().strftime("%Y-%m")
        self._build()

    def _build(self):
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
            text="Voici ton résumé financier",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).grid(row=1, column=0, sticky="w")

        # ── Sélecteur de mois ─────────────────────────────────
        month_row = ctk.CTkFrame(self, fg_color="transparent")
        month_row.grid(row=1, column=0, sticky="ew", padx=24, pady=(14, 0))

        ctk.CTkLabel(
            month_row, text="Mois affiché :",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(side="left", padx=(0, 8))

        months = get_available_months(state.current_user_id)
        if not months:
            months = [self.current_month]

        # S'assurer que le mois courant est dans la liste
        if self.current_month not in months:
            months = [self.current_month] + months

        self.month_var = ctk.StringVar(value=self.current_month)
        self.month_menu = ctk.CTkOptionMenu(
            month_row,
            values=months,
            variable=self.month_var,
            command=self._on_month_change,
            width=140, height=30,
            fg_color="#1D9E75",
            button_color="#0F6E56",
            button_hover_color="#085041",
            text_color="white",
            font=ctk.CTkFont(size=12),
        )
        self.month_menu.pack(side="left")

        # ── Card solde cumulé (pleine largeur) ────────────────
        self.card_cumul_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.card_cumul_frame.grid(
            row=2, column=0, sticky="ew", padx=24, pady=(14, 0)
        )
        self.card_cumul_frame.columnconfigure(0, weight=1)

        # ── Cards mensuelles (4 colonnes) ─────────────────────
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(
            row=3, column=0, sticky="ew", padx=24, pady=(10, 0)
        )
        for i in range(4):
            self.cards_frame.columnconfigure(i, weight=1)

        # ── Dernières transactions ─────────────────────────────
        tx_header = ctk.CTkFrame(self, fg_color="transparent")
        tx_header.grid(row=4, column=0, sticky="ew", padx=24, pady=(16, 4))
        ctk.CTkLabel(
            tx_header,
            text="Dernières transactions",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            tx_header,
            text="(toutes dates)",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).pack(side="left", padx=6)

        self.tx_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=180
        )
        self.tx_frame.grid(
            row=5, column=0, sticky="ew", padx=24, pady=(0, 16)
        )
        self.tx_frame.columnconfigure(0, weight=1)

        self._build_cumul_card()
        self._build_cards()
        self._build_transactions()
        from ui.onboarding import show_onboarding
        show_onboarding(self, "dashboard")

    def _get_fmt(self):
        config  = get_config()
        api_key = config.get("api_key", "")
        base    = config.get("devise_base", "EUR")
        cible   = config.get("devise", "EUR")
        symbole = config.get("symbole", "€")

        def fmt(amount):
            converted = convert(amount, base, cible) if api_key else amount
            return f"{converted:.2f} {symbole}"

        return fmt, symbole

    def _build_cumul_card(self):
        for w in self.card_cumul_frame.winfo_children():
            w.destroy()

        fmt, symbole = self._get_fmt()
        balance = get_total_balance(state.current_user_id)

        card = ctk.CTkFrame(
            self.card_cumul_frame,
            fg_color="#0f172a",
            corner_radius=10,
        )
        card.grid(row=0, column=0, sticky="ew")
        card.columnconfigure(1, weight=1)

        # Pastille colorée
        color = "#5DCAA5" if balance >= 0 else "#F09595"
        ctk.CTkLabel(
            card, text="",
            width=6, height=48,
            fg_color=color,
            corner_radius=3,
        ).grid(row=0, column=0, padx=(12, 10), pady=12, rowspan=2)

        ctk.CTkLabel(
            card, text="Solde cumulé total",
            font=ctk.CTkFont(size=11),
            text_color="gray", anchor="w",
        ).grid(row=0, column=1, sticky="w", pady=(12, 0))

        ctk.CTkLabel(
            card,
            text=f"{'+' if balance >= 0 else ''}{fmt(balance)}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=color, anchor="w",
        ).grid(row=1, column=1, sticky="w", pady=(0, 12))

        ctk.CTkLabel(
            card,
            text="Depuis le début · toutes transactions confondues",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        ).grid(row=0, column=2, rowspan=2, padx=16, pady=12, sticky="e")

    def _build_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        fmt, symbole = self._get_fmt()
        summary = get_monthly_summary(
            state.current_user_id, self.current_month
        )

        cards_data = [
            ("Solde du mois",
             f"{'+' if summary['solde'] >= 0 else ''}{fmt(summary['solde'])}",
             "#5DCAA5" if summary["solde"] >= 0 else "#F09595"),
            ("Dépenses",
             fmt(summary["total_depenses"]),
             "#F09595"),
            ("Revenus",
             fmt(summary["total_revenus"]),
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
            card.grid(
                row=0, column=i,
                padx=(0, 8) if i < 3 else (0, 0),
                sticky="ew",
            )
            card.columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card, text=label,
                font=ctk.CTkFont(size=11),
                text_color="gray",
            ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))

            ctk.CTkLabel(
                card, text=value,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color,
            ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 4))

            # Mois affiché en petit sous la valeur
            ctk.CTkLabel(
                card, text=self.current_month,
                font=ctk.CTkFont(size=9),
                text_color="gray",
            ).grid(row=2, column=0, sticky="w", padx=14, pady=(0, 10))

    def _build_transactions(self):
        for w in self.tx_frame.winfo_children():
            w.destroy()

        transactions = get_last_transactions(
            state.current_user_id, limit=5
        )

        if not transactions:
            ctk.CTkLabel(
                self.tx_frame,
                text="Aucune transaction pour l'instant\nClique sur Ajouter pour commencer !",
                text_color="gray",
                font=ctk.CTkFont(size=12),
                justify="center",
            ).grid(row=0, column=0, pady=30)
            return

        config  = get_config()
        api_key = config.get("api_key", "")
        base    = config.get("devise_base", "EUR")
        cible   = config.get("devise", "EUR")
        symbole = config.get("symbole", "€")

        for i, tx in enumerate(transactions):
            row = ctk.CTkFrame(
                self.tx_frame,
                fg_color="#16213e" if i % 2 == 0 else "transparent",
                corner_radius=8,
            )
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.columnconfigure(1, weight=1)

            color = tx.get("color") or "#5F5E5A"
            ctk.CTkLabel(
                row, text="",
                width=28, height=28,
                fg_color=color, corner_radius=6,
            ).grid(row=0, column=0, padx=(10, 8), pady=8, rowspan=2)

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
                text_color="gray", anchor="w",
            ).grid(row=1, column=1, sticky="w", pady=(0, 8))

            ctk.CTkLabel(
                row, text=tx.get("date", ""),
                font=ctk.CTkFont(size=10),
                text_color="gray",
            ).grid(row=0, column=2, padx=10, pady=(8, 0))

            is_dep  = tx.get("type") == "depense"
            montant = convert(tx["amount"], base, cible) if api_key else tx["amount"]
            txt     = f"-{montant:.2f} {symbole}" if is_dep else f"+{montant:.2f} {symbole}"

            ctk.CTkLabel(
                row, text=txt,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#F09595" if is_dep else "#5DCAA5",
            ).grid(row=0, column=3, padx=(0, 14), pady=(8, 0))

    def _on_month_change(self, month):
        self.current_month = month
        self._build_cards()

    def refresh(self):
        months = get_available_months(state.current_user_id)
        if self.current_month not in months:
            months = [self.current_month] + months
        
        # Mettre à jour le widget CTkOptionMenu, pas le StringVar
        self.month_menu.configure(values=months)

        self._build_cumul_card()
        self._build_cards()
        self._build_transactions()