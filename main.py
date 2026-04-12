import customtkinter as ctk
from database.models import create_tables
from ui.app import App

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    create_tables()
    app = App()
    app.mainloop()