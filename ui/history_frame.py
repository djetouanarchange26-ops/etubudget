import customtkinter as ctk
from datetime import datetime
import state
from utils.config import get_config
from utils.currency import convert
from database.queries import (
    get_transactions,
    get_categories_for_user,
    get_available_months,
    update_transaction,
    delete_transaction,
)


class HistoryFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.selected_month = None
        self.selected_category_id = None
        self.selected_type = None
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        # ── En-tête ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        ctk.CTkLabel(
            header, text="Historique",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Toutes tes transactions avec filtres",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        # ── Filtres ───────────────────────────────────────────
        filters = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        filters.grid(row=1, column=0, sticky="ew", padx=24, pady=(14, 0))
        filters.columnconfigure((0, 1, 2), weight=1)

        # Filtre mois
        ctk.CTkLabel(
            filters, text="Mois",
            font=ctk.CTkFont(size=11), text_color="gray",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))

        months = get_available_months(state.current_user_id)
        month_values = ["Tous les mois"] + months

        self.month_var = ctk.StringVar(value="Tous les mois")
        ctk.CTkOptionMenu(
            filters,
            values=month_values,
            variable=self.month_var,
            command=lambda _: self._apply_filters(),
            height=32, fg_color="#0f172a",
            button_color="#1D9E75",
            button_hover_color="#0F6E56",
            text_color="white",
        ).grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))

        # Filtre catégorie
        ctk.CTkLabel(
            filters, text="Catégorie",
            font=ctk.CTkFont(size=11), text_color="gray",
        ).grid(row=0, column=1, sticky="w", padx=14, pady=(10, 2))

        categories = get_categories_for_user(state.current_user_id)
        self.categories_map = {cat["name"]: cat["id"] for cat in categories}
        cat_values = ["Toutes"] + list(self.categories_map.keys())

        self.cat_var = ctk.StringVar(value="Toutes")
        ctk.CTkOptionMenu(
            filters,
            values=cat_values,
            variable=self.cat_var,
            command=lambda _: self._apply_filters(),
            height=32, fg_color="#0f172a",
            button_color="#1D9E75",
            button_hover_color="#0F6E56",
            text_color="white",
        ).grid(row=1, column=1, sticky="ew", padx=14, pady=(0, 12))

        # Filtre type
        ctk.CTkLabel(
            filters, text="Type",
            font=ctk.CTkFont(size=11), text_color="gray",
        ).grid(row=0, column=2, sticky="w", padx=14, pady=(10, 2))

        self.type_var = ctk.StringVar(value="Tous")
        ctk.CTkOptionMenu(
            filters,
            values=["Tous", "depense", "revenu"],
            variable=self.type_var,
            command=lambda _: self._apply_filters(),
            height=32, fg_color="#0f172a",
            button_color="#1D9E75",
            button_hover_color="#0F6E56",
            text_color="white",
        ).grid(row=1, column=2, sticky="ew", padx=14, pady=(0, 12))

        # ── Liste ─────────────────────────────────────────────
        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=300,
        )
        self.list_frame.grid(
            row=2, column=0, sticky="ew", padx=24, pady=(12, 0)
        )
        self.list_frame.columnconfigure(0, weight=1)

        # ── Total ─────────────────────────────────────────────
        self.total_frame = ctk.CTkFrame(
            self, fg_color="#16213e", corner_radius=8
        )
        self.total_frame.grid(
            row=3, column=0, sticky="ew", padx=24, pady=(8, 16)
        )
        self.total_frame.columnconfigure(0, weight=1)

        self.label_total = ctk.CTkLabel(
            self.total_frame, text="",
            font=ctk.CTkFont(size=12), text_color="gray",
        )
        self.label_total.grid(row=0, column=0, sticky="e", padx=16, pady=8)

        self._apply_filters()
        from ui.onboarding import show_onboarding
        show_onboarding(self, "historique")

    def _apply_filters(self):
        month = self.month_var.get()
        cat_name = self.cat_var.get()
        tx_type = self.type_var.get()

        month_filter    = None if month == "Tous les mois" else month
        cat_filter      = self.categories_map.get(cat_name) if cat_name != "Toutes" else None
        type_filter     = None if tx_type == "Tous" else tx_type

        transactions = get_transactions(
            state.current_user_id,
            month=month_filter,
            category_id=cat_filter,
            tx_type=type_filter,
        )
        self._build_list(transactions)
        self._update_total(transactions)

    def _build_list(self, transactions):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not transactions:
            ctk.CTkLabel(
                self.list_frame,
                text="Aucune transaction pour ces filtres.\nEssaie de changer le mois ou la catégorie.",
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
                self.list_frame,
                fg_color="#16213e" if i % 2 == 0 else "transparent",
                corner_radius=8,
            )
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.columnconfigure(1, weight=1)

            # Pastille couleur
            color = tx.get("category_color") or "#5F5E5A"
            ctk.CTkLabel(
                row, text="",
                width=24, height=24,
                fg_color=color, corner_radius=6,
            ).grid(row=0, column=0, padx=(12, 8), pady=10, rowspan=2)

            # Description + catégorie
            ctk.CTkLabel(
                row,
                text=tx.get("description") or "Sans description",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
            ).grid(row=0, column=1, sticky="w", pady=(8, 0))

            ctk.CTkLabel(
                row,
                text=tx.get("category_name") or "Sans catégorie",
                font=ctk.CTkFont(size=10), text_color="gray",
                anchor="w",
            ).grid(row=1, column=1, sticky="w", pady=(0, 8))

            # Date
            ctk.CTkLabel(
                row, text=tx.get("date", ""),
                font=ctk.CTkFont(size=10), text_color="gray",
            ).grid(row=0, column=2, padx=10, pady=(8, 0))

            # Montant converti
            montant = convert(tx["amount"], base, cible) if api_key else tx["amount"]
            is_dep  = tx.get("type") == "depense"
            txt     = f"-{montant:.2f} {symbole}" if is_dep else f"+{montant:.2f} {symbole}"
            ctk.CTkLabel(
                row, text=txt,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#F09595" if is_dep else "#5DCAA5",
            ).grid(row=0, column=3, padx=(0, 6))

            # Boutons modifier / supprimer
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.grid(row=0, column=4, rowspan=2, padx=(0, 12), pady=8)

            ctk.CTkButton(
                btn_frame, text="Modifier",
                width=70, height=26,
                fg_color="transparent",
                border_width=1, border_color="#534AB7",
                text_color="#AFA9EC",
                hover_color="#534AB7",
                font=ctk.CTkFont(size=10),
                command=lambda t=tx: self._open_edit(t),
            ).pack(pady=(0, 4))

            ctk.CTkButton(
                btn_frame, text="Supprimer",
                width=70, height=26,
                fg_color="transparent",
                border_width=1, border_color="#993C1D",
                text_color="#F09595",
                hover_color="#993C1D",
                font=ctk.CTkFont(size=10),
                command=lambda tid=tx["id"]: self._confirm_delete(tid),
            ).pack()

    def _update_total(self, transactions):
        if not transactions:
            self.label_total.configure(text="Aucune transaction")
            return

        config  = get_config()
        api_key = config.get("api_key", "")
        base    = config.get("devise_base", "EUR")
        cible   = config.get("devise", "EUR")
        symbole = config.get("symbole", "€")

        total_dep = sum(
            convert(t["amount"], base, cible) if api_key else t["amount"]
            for t in transactions if t["type"] == "depense"
        )
        total_rev = sum(
            convert(t["amount"], base, cible) if api_key else t["amount"]
            for t in transactions if t["type"] == "revenu"
        )
        self.label_total.configure(
            text=f"{len(transactions)} transaction(s)  —  "
                 f"Dépenses : {total_dep:.2f} {symbole}  |  "
                 f"Revenus : {total_rev:.2f} {symbole}"
        )

    def _confirm_delete(self, tx_id):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmer la suppression")
        dialog.geometry("320x140")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Supprimer cette transaction ?",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(pady=(24, 6))

        ctk.CTkLabel(
            dialog, text="Cette action est irréversible.",
            font=ctk.CTkFont(size=11), text_color="gray",
        ).pack(pady=(0, 16))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row, text="Annuler",
            width=110, height=32,
            fg_color="transparent",
            border_width=1, border_color="#3a3a5a",
            command=dialog.destroy,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text="Supprimer",
            width=110, height=32,
            fg_color="#993C1D", hover_color="#712B13",
            command=lambda: self._delete(tx_id, dialog),
        ).pack(side="left", padx=8)

    def _delete(self, tx_id, dialog):
        dialog.destroy()
        delete_transaction(tx_id, state.current_user_id)
        self._apply_filters()
        if "accueil" in self.app.frames:
            self.app.frames["accueil"].refresh()

    def _open_edit(self, tx):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Modifier la transaction")
        dialog.geometry("400x380")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Modifier la transaction",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(20, 14))

        # Type
        type_var = ctk.StringVar(value=tx.get("type", "depense"))
        ctk.CTkSegmentedButton(
            dialog,
            values=["depense", "revenu"],
            variable=type_var,
            selected_color="#1D9E75",
            selected_hover_color="#0F6E56",
            unselected_color="#0f172a",
            text_color="white",
        ).pack(padx=20, fill="x", pady=(0, 10))

        # Montant
        entry_amount = ctk.CTkEntry(
            dialog, placeholder_text="Montant", height=36
        )
        entry_amount.pack(padx=20, fill="x", pady=(0, 8))
        entry_amount.insert(0, str(tx["amount"]))

        # Date
        entry_date = ctk.CTkEntry(
            dialog, placeholder_text="JJ/MM/AAAA", height=36
        )
        entry_date.pack(padx=20, fill="x", pady=(0, 8))
        # Convertir YYYY-MM-DD → JJ/MM/AAAA pour l'affichage
        try:
            from datetime import datetime
            d = datetime.strptime(tx["date"], "%Y-%m-%d")
            entry_date.insert(0, d.strftime("%d/%m/%Y"))
        except Exception:
            entry_date.insert(0, tx["date"])

        # Description
        entry_desc = ctk.CTkEntry(
            dialog, placeholder_text="Description", height=36
        )
        entry_desc.pack(padx=20, fill="x", pady=(0, 8))
        entry_desc.insert(0, tx.get("description") or "")

        label_err = ctk.CTkLabel(
            dialog, text="", font=ctk.CTkFont(size=11),
            text_color="#E24B4A"
        )
        label_err.pack()

        def save():
            from utils.validators import validate_transaction_fields
            ok, msg, amount, date_iso = validate_transaction_fields(
                entry_amount.get(), entry_date.get()
            )
            if not ok:
                label_err.configure(text=msg)
                return
            update_transaction(
                tx["id"], state.current_user_id,
                amount, entry_desc.get().strip(),
                date_iso, type_var.get(),
                tx.get("category_id"),
            )
            dialog.destroy()
            self._apply_filters()
            if "accueil" in self.app.frames:
                self.app.frames["accueil"].refresh()

        ctk.CTkButton(
            dialog, text="Sauvegarder",
            height=38, fg_color="#1D9E75",
            hover_color="#0F6E56",
            command=save,
        ).pack(padx=20, fill="x", pady=(8, 0))

    def refresh(self):
        self._apply_filters()