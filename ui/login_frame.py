import customtkinter as ctk

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        ctk.CTkLabel(self, text="Login — à construire en S3").pack(pady=40)