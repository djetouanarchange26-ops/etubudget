import customtkinter as ctk
from datetime import datetime
import state
from utils.validators import validate_transaction_fields
from database.queries import insert_transaction, get_categories_for_user


class AddTransactionFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.selected_category_id = None
        self.category_buttons = {}
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        # ── En-tête ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        ctk.CTkLabel(
            header, text="Nouvelle transaction",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Saisie rapide — description optionnelle",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        # ── Formulaire ────────────────────────────────────────
        form = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        form.grid(row=1, column=0, sticky="ew", padx=24, pady=20)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        # Type (segmented button)
        ctk.CTkLabel(
            form, text="Type",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 4))

        self.type_var = ctk.StringVar(value="depense")
        ctk.CTkSegmentedButton(
            form,
            values=["depense", "revenu"],
            variable=self.type_var,
            selected_color="#1D9E75",
            selected_hover_color="#0F6E56",
            unselected_color="#0f172a",
            unselected_hover_color="#1a2744",
            text_color="white",
            width=400,
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 12))

        # Montant
        ctk.CTkLabel(
            form, text="Montant",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 4))

        self.entry_amount = ctk.CTkEntry(
            form, placeholder_text="ex : 12,50",
            height=38, width=200,
        )
        self.entry_amount.grid(row=3, column=0, sticky="w", padx=16, pady=(0, 12))

        # Date
        ctk.CTkLabel(
            form, text="Date",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).grid(row=2, column=1, sticky="w", padx=16, pady=(0, 4))

        self.entry_date = ctk.CTkEntry(
            form, placeholder_text="JJ/MM/AAAA",
            height=38, width=200,
        )
        self.entry_date.grid(row=3, column=1, sticky="w", padx=16, pady=(0, 12))
        # Pré-remplir avec aujourd'hui
        self.entry_date.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Description
        ctk.CTkLabel(
            form, text="Description (optionnel)",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 4))

        self.entry_desc = ctk.CTkEntry(
            form, placeholder_text="ex : Monoprix — courses semaine",
            height=38,
        )
        self.entry_desc.grid(
            row=5, column=0, columnspan=2,
            sticky="ew", padx=16, pady=(0, 12)
        )

        # Catégories
        ctk.CTkLabel(
            form, text="Catégorie",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).grid(row=6, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 8))

        self.chips_frame = ctk.CTkFrame(form, fg_color="transparent")
        self.chips_frame.grid(
            row=7, column=0, columnspan=2,
            sticky="ew", padx=16, pady=(0, 12)
        )
        self._build_chips()

        # Label erreur/succès
        self.label_feedback = ctk.CTkLabel(
            form, text="",
            font=ctk.CTkFont(size=12),
        )
        self.label_feedback.grid(
            row=8, column=0, columnspan=2,
            sticky="w", padx=16, pady=(0, 4)
        )

        # Bouton valider
        ctk.CTkButton(
            form, text="Enregistrer la transaction",
            height=42, fg_color="#1D9E75",
            hover_color="#0F6E56",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._submit,
        ).grid(row=9, column=0, columnspan=2,
               sticky="ew", padx=16, pady=(0, 16))
        self.bind("<Return>", lambda e: self._submit())
        from ui.onboarding import show_onboarding
        show_onboarding(self, "ajouter")

    def _build_chips(self):
        for widget in self.chips_frame.winfo_children():
            widget.destroy()
        self.category_buttons = {}
        self.selected_category_id = None

        categories = get_categories_for_user(state.current_user_id)

        if not categories:
            ctk.CTkLabel(
                self.chips_frame,
                text="Aucune catégorie — crée-en dans Paramètres",
                font=ctk.CTkFont(size=11), text_color="gray",
            ).pack(side="left")
            return

        for i, cat in enumerate(categories):
            btn = ctk.CTkButton(
                self.chips_frame,
                text=cat["name"],
                height=30, width=90,
                corner_radius=15,
                fg_color="#0f172a",
                hover_color="#1D9E75",
                border_width=1,
                border_color="#3a3a5a",
                text_color="white",
                font=ctk.CTkFont(size=11),
                command=lambda c=cat: self._select_category(c),
            )
            btn.grid(row=i // 4, column=i % 4, padx=4, pady=4)
            self.category_buttons[cat["id"]] = btn

    def _select_category(self, cat):
        # Désélectionner toutes les chips
        for btn in self.category_buttons.values():
            btn.configure(fg_color="#0f172a", border_color="#3a3a5a")

        if self.selected_category_id == cat["id"]:
            # Désélectionner si on reclique sur la même
            self.selected_category_id = None
        else:
            # Sélectionner la nouvelle
            self.selected_category_id = cat["id"]
            color = cat.get("color") or "#1D9E75"
            self.category_buttons[cat["id"]].configure(
                fg_color=color, border_color=color
            )

    def _submit(self):
        ok, msg, amount, date_iso = validate_transaction_fields(
            self.entry_amount.get(),
            self.entry_date.get(),
        )
        if not ok:
            self.label_feedback.configure(text=msg, text_color="#E24B4A")
            return

        success = insert_transaction(
            user_id=state.current_user_id,
            amount=amount,
            description=self.entry_desc.get().strip(),
            date=date_iso,
            tx_type=self.type_var.get(),
            category_id=self.selected_category_id,
        )

        if success:
            self.label_feedback.configure(
                text="Transaction enregistrée !", text_color="#5DCAA5"
            )
            self._reset_form()
            # Rafraîchir le dashboard
            if "accueil" in self.app.frames:
                self.app.frames["accueil"].refresh()
            # Effacer le message après 2 secondes
            self.after(2000, lambda: self.label_feedback.configure(text=""))
        else:
            self.label_feedback.configure(
                text="Erreur lors de l'enregistrement.",
                text_color="#E24B4A"
            )

    def _reset_form(self):
        self.entry_amount.delete(0, "end")
        self.entry_desc.delete(0, "end")
        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.type_var.set("depense")
        for btn in self.category_buttons.values():
            btn.configure(fg_color="#0f172a", border_color="#3a3a5a")
        self.selected_category_id = None

    def refresh(self):
        self._build_chips()