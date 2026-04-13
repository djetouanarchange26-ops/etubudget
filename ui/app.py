import customtkinter as ctk
import state
from utils.config import get_config, save_config, DEVISES


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EtuBudget")
        self.geometry("900x600")
        self.minsize(800, 500)
        self.frames = {}
        self.current_frame = None
        self.nav_buttons = {}
        self._build_layout()
        self._register_frames()
        self.show_frame("login")
        self.bind("<Control-n>", lambda e: self.show_frame("ajouter"))
        self.bind("<Control-n>", lambda e: self.show_frame("ajouter"))
        self.bind("<Control-h>", lambda e: self.show_frame("historique"))
        self.bind("<Control-s>", lambda e: self.show_frame("stats"))
        self.bind("<Control-e>", lambda e: self.show_frame("exporter"))
        self.bind("<Control-d>", lambda e: self.show_frame("accueil"))

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0,
                                    fg_color="#16213e")
        self.sidebar.pack_propagate(False)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True)

    def _build_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self.nav_buttons = {}

        # ── Logo + titre ──────────────────────────────────────
        top = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(20, 16))

        ctk.CTkLabel(
            top, text="E", width=36, height=36,
            fg_color="#1D9E75", corner_radius=10,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
        ).pack(side="left")

        ctk.CTkLabel(
            top, text="EtuBudget",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="white",
        ).pack(side="left", padx=8)

        # ── Boutons navigation ────────────────────────────────
        nav_items = [
            ("accueil",    "Accueil"),
            ("ajouter",    "Ajouter"),
            ("categories", "Catégories"),
            ("historique", "Historique"),
            ("stats",      "Statistiques"),
            ("exporter",   "Exporter"),
        ]
        for name, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label,
                anchor="w", height=38,
                fg_color="transparent",
                hover_color="#0F6E56",
                text_color="white",
                corner_radius=8,
                command=lambda n=name: self.show_frame(n),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[name] = btn

        # ── Bloc bas (devise + utilisateur) ───────────────────
        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=10, pady=16)

        # Séparateur
        ctk.CTkFrame(
            bottom, height=1, fg_color="#2a2a4a"
        ).pack(fill="x", pady=(0, 12))

        # Sélecteur de devise
        config = get_config()

        ctk.CTkLabel(
            bottom, text="Devise",
            font=ctk.CTkFont(size=11),
            text_color="#9090a8",
        ).pack(anchor="w", pady=(0, 4))

        devise_var = ctk.StringVar(value=config.get("devise", "EUR"))

        def on_devise_change(choix):
            c = get_config()
            c["devise"]  = choix
            c["symbole"] = DEVISES[choix]
            save_config(c)
            if self.current_frame == "accueil" and "accueil" in self.frames:
                self.frames["accueil"].refresh()

        ctk.CTkOptionMenu(
            bottom,
            values=list(DEVISES.keys()),
            variable=devise_var,
            command=on_devise_change,
            width=176, height=32,
            fg_color="#1D9E75",
            button_color="#0F6E56",
            button_hover_color="#085041",
            text_color="white",
            font=ctk.CTkFont(size=12),
        ).pack(fill="x", pady=(0, 10))

        # Bloc utilisateur
        user_row = ctk.CTkFrame(bottom, fg_color="transparent")
        user_row.pack(fill="x")

        username = state.current_username or "?"
        initials = username[:2].upper()

        ctk.CTkLabel(
            user_row, text=initials,
            width=32, height=32,
            fg_color="#534AB7", corner_radius=16,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
        ).pack(side="left")

        ctk.CTkLabel(
            user_row, text=username,
            font=ctk.CTkFont(size=12),
            text_color="#c8c8d8",
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            bottom, text="Déconnexion",
            height=32, fg_color="transparent",
            border_width=1, border_color="#3a3a5a",
            text_color="#c8c8d8",
            hover_color="#993C1D",
            command=self.logout,
        ).pack(fill="x", pady=(10, 0))

    def _register_frames(self):
        from ui.login_frame import LoginFrame
        self.frames["login"] = LoginFrame(self.container, self)

    def _set_active_nav(self, name):
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(fg_color="#1D9E75")
            else:
                btn.configure(fg_color="transparent")

    def show_frame(self, name: str):
        # Créer la frame si elle n'existe pas encore
        if name not in self.frames:
            if name == "accueil":
                from ui.dashboard_frame import DashboardFrame
                self.frames["accueil"] = DashboardFrame(self.container, self)
            elif name == "ajouter":
                from ui.add_transaction_frame import AddTransactionFrame
                self.frames["ajouter"] = AddTransactionFrame(self.container, self)
            elif name == "categories":
                from ui.categories_frame import CategoriesFrame
                self.frames["categories"] = CategoriesFrame(self.container, self)
            elif name == "historique":
                from ui.history_frame import HistoryFrame
                self.frames["historique"] = HistoryFrame(self.container, self)
        
            elif name == "stats":
                from ui.stats_frame import StatsFrame
                self.frames["stats"] = StatsFrame(self.container, self)
            elif name == "exporter":
                from ui.export_frame import ExportFrame
                self.frames["exporter"] = ExportFrame(self.container, self)

        # Cacher toutes les frames
        for frame in self.frames.values():
            frame.pack_forget()

        # Sidebar
        if name == "login":
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side="left", fill="y")
            self._build_sidebar()
            self._set_active_nav(name)

        # Afficher la frame demandée
        if name in self.frames:
            self.frames[name].pack(fill="both", expand=True)

        self.current_frame = name

    def register_frame(self, name: str, frame):
        self.frames[name] = frame

    def logout(self):
        state.clear_user()
        for widget in self.container.winfo_children():
            widget.destroy()
        self.frames = {}
        self._register_frames()
        self.show_frame("login")