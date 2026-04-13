import customtkinter as ctk
import state
from database.queries import (
    get_categories_for_user,
    insert_category,
    delete_category,
)

PALETTE = [
    "#1D9E75", "#5DCAA5", "#534AB7", "#AFA9EC",
    "#854F0B", "#EF9F27", "#993C1D", "#F09595",
    "#185FA5", "#85B7EB", "#3B6D11", "#97C459",
    "#5F5E5A", "#D3D1C7", "#D4537E", "#ED93B1",
]


class CategoriesFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.selected_color = PALETTE[0]
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        # ── En-tête ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        ctk.CTkLabel(
            header, text="Catégories",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Crée et gère tes catégories de dépenses",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        # ── Formulaire création ───────────────────────────────
        form = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        form.grid(row=1, column=0, sticky="ew", padx=24, pady=(16, 0))
        form.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            form, text="Nouvelle catégorie",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=3,
               sticky="w", padx=16, pady=(14, 8))

        # Champ nom
        self.entry_name = ctk.CTkEntry(
            form, placeholder_text="Nom de la catégorie",
            height=36, width=220,
        )
        self.entry_name.grid(row=1, column=0, padx=16, pady=(0, 12))

        # Palette de couleurs
        palette_frame = ctk.CTkFrame(form, fg_color="transparent")
        palette_frame.grid(row=1, column=1, sticky="w", padx=8, pady=(0, 12))

        self.color_buttons = {}
        for i, color in enumerate(PALETTE):
            btn = ctk.CTkButton(
                palette_frame,
                text="",
                width=24, height=24,
                corner_radius=6,
                fg_color=color,
                hover_color=color,
                border_width=2,
                border_color=color,
                command=lambda c=color: self._select_color(c),
            )
            btn.grid(row=i // 8, column=i % 8, padx=2, pady=2)
            self.color_buttons[color] = btn

        # Marquer la première couleur comme sélectionnée
        self._select_color(PALETTE[0])

        # Label feedback
        self.label_feedback = ctk.CTkLabel(
            form, text="", font=ctk.CTkFont(size=11),
        )
        self.label_feedback.grid(
            row=2, column=0, columnspan=3,
            sticky="w", padx=16, pady=(0, 4)
        )

        # Bouton créer
        ctk.CTkButton(
            form, text="Créer la catégorie",
            height=36, width=180,
            fg_color="#1D9E75", hover_color="#0F6E56",
            command=self._create,
        ).grid(row=3, column=0, sticky="w", padx=16, pady=(0, 14))

        # ── Liste des catégories ──────────────────────────────
        ctk.CTkLabel(
            self,
            text="Mes catégories",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=2, column=0, sticky="w", padx=24, pady=(20, 6))

        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=240,
        )
        self.list_frame.grid(
            row=3, column=0, sticky="ew", padx=24, pady=(0, 16)
        )
        self.list_frame.columnconfigure(0, weight=1)

        self._build_list()
        self.bind("<Return>", lambda e: self._create())
        from ui.onboarding import show_onboarding
        show_onboarding(self, "categories")

    def _select_color(self, color):
        # Réinitialiser tous les boutons
        for c, btn in self.color_buttons.items():
            btn.configure(border_color=c, border_width=2)
        # Mettre en évidence la couleur sélectionnée
        self.color_buttons[color].configure(
            border_color="white", border_width=3
        )
        self.selected_color = color

    def _create(self):
        name = self.entry_name.get().strip()
        if not name:
            self.label_feedback.configure(
                text="Le nom est obligatoire.", text_color="#E24B4A"
            )
            return
        if len(name) < 2:
            self.label_feedback.configure(
                text="Nom trop court — 2 caractères minimum.",
                text_color="#E24B4A"
            )
            return

        ok, msg = insert_category(
            state.current_user_id, name, self.selected_color
        )
        if not ok:
            self.label_feedback.configure(text=msg, text_color="#E24B4A")
            return

        self.label_feedback.configure(
            text=f"Catégorie '{name}' créée !", text_color="#5DCAA5"
        )
        self.entry_name.delete(0, "end")
        self._select_color(PALETTE[0])
        self._build_list()
        self.after(2000, lambda: self.label_feedback.configure(text=""))

        # Rafraîchir les chips dans add_transaction si la frame existe
        if "ajouter" in self.app.frames:
            self.app.frames["ajouter"].refresh()

    def _build_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        categories = get_categories_for_user(state.current_user_id)

        if not categories:
            ctk.CTkLabel(
                self.list_frame,
                text="Aucune catégorie pour l'instant.\nClique sur Créer pour en ajouter une !",
                text_color="gray",
                font=ctk.CTkFont(size=12),
                justify="center",
            ).grid(row=0, column=0, pady=30)
            return

        for i, cat in enumerate(categories):
            row = ctk.CTkFrame(
                self.list_frame,
                fg_color="#16213e" if i % 2 == 0 else "transparent",
                corner_radius=8,
            )
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.columnconfigure(1, weight=1)

            # Pastille couleur
            ctk.CTkLabel(
                row, text="",
                width=24, height=24,
                fg_color=cat["color"],
                corner_radius=6,
            ).grid(row=0, column=0, padx=(12, 8), pady=10)

            # Nom
            ctk.CTkLabel(
                row, text=cat["name"],
                font=ctk.CTkFont(size=13),
                anchor="w",
            ).grid(row=0, column=1, sticky="w", pady=10)

            # Bouton supprimer
            ctk.CTkButton(
                row, text="Supprimer",
                width=90, height=28,
                fg_color="transparent",
                border_width=1,
                border_color="#993C1D",
                text_color="#F09595",
                hover_color="#993C1D",
                font=ctk.CTkFont(size=11),
                command=lambda cid=cat["id"]: self._confirm_delete(cid, cat["name"]),
            ).grid(row=0, column=2, padx=12, pady=10)

    def _confirm_delete(self, category_id, name):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmer la suppression")
        dialog.geometry("360x160")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"Supprimer la catégorie '{name}' ?",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(pady=(24, 6))

        ctk.CTkLabel(
            dialog,
            text="Les transactions liées ne seront pas supprimées.",
            font=ctk.CTkFont(size=11), text_color="gray",
        ).pack(pady=(0, 16))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row, text="Annuler",
            width=120, height=34,
            fg_color="transparent",
            border_width=1, border_color="#3a3a5a",
            command=dialog.destroy,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text="Supprimer",
            width=120, height=34,
            fg_color="#993C1D", hover_color="#712B13",
            command=lambda: self._delete(category_id, dialog),
        ).pack(side="left", padx=8)

    def _delete(self, category_id, dialog):
        dialog.destroy()
        ok, msg = delete_category(category_id, state.current_user_id)
        if ok:
            self._build_list()
            if "ajouter" in self.app.frames:
                self.app.frames["ajouter"].refresh()

    def refresh(self):
        self._build_list()