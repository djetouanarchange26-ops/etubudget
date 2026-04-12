import customtkinter as ctk
import state

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EtuBudget")
        self.geometry("900x600")
        self.minsize(800, 500)
        self.frames = {}
        self.current_frame = None
        self._build_layout()
        self._register_frames()
        self.show_frame("login")

    def _build_layout(self):
        # Sidebar gauche (sera peuplée en S4)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack_propagate(False)
        # Zone principale droite
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True)
        # La sidebar sera affichée seulement après le login
        # (on la cache pour l'instant)

    def _register_frames(self):
        # On importe ici pour éviter les imports circulaires
        from ui.login_frame import LoginFrame
        self.frames["login"] = LoginFrame(self.container, self)
        # Les autres frames seront ajoutées au fur et à mesure des semaines

    def show_frame(self, name: str):
        # Cache toutes les frames
        for frame in self.frames.values():
            frame.pack_forget()
        # Gestion de la sidebar : visible uniquement si connecté
        if name == "login":
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side="left", fill="y")
        # Affiche la frame demandée
        self.frames[name].pack(fill="both", expand=True)
        self.current_frame = name

    def register_frame(self, name: str, frame):
        """Permet d'enregistrer une frame depuis l'extérieur (utile en S4+)."""
        self.frames[name] = frame

    def logout(self):
        state.clear_user()
        self.show_frame("login")