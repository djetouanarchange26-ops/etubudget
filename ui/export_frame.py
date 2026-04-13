import customtkinter as ctk
import os
import subprocess
import sys
from tkinter import filedialog
from datetime import datetime
import state
from utils.config import get_config
from utils.export import export_to_csv, export_to_pdf
from database.queries import get_transactions, get_available_months


class ExportFrame(ctk.CTkFrame):
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
        ctk.CTkLabel(
            header, text="Exporter",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Télécharge ton historique en CSV ou PDF",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        # ── Sélecteur de période ──────────────────────────────
        period_card = ctk.CTkFrame(
            self, fg_color="#16213e", corner_radius=10
        )
        period_card.grid(
            row=1, column=0, sticky="ew", padx=24, pady=(16, 0)
        )
        period_card.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            period_card,
            text="Période à exporter",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=2,
               sticky="w", padx=16, pady=(14, 8))

        ctk.CTkLabel(
            period_card, text="Mois :",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 14))

        months = get_available_months(state.current_user_id)
        if not months:
            months = [self.current_month]
        all_months = ["Toutes les transactions"] + months

        self.period_var = ctk.StringVar(value=all_months[0])
        ctk.CTkOptionMenu(
            period_card,
            values=all_months,
            variable=self.period_var,
            width=220, height=34,
            fg_color="#1D9E75",
            button_color="#0F6E56",
            button_hover_color="#085041",
            text_color="white",
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=1, sticky="w", padx=8, pady=(0, 14))

        # ── Deux panneaux export ──────────────────────────────
        panels = ctk.CTkFrame(self, fg_color="transparent")
        panels.grid(row=2, column=0, sticky="ew", padx=24, pady=(16, 0))
        panels.columnconfigure(0, weight=1)
        panels.columnconfigure(1, weight=1)

        # ── Panneau CSV ───────────────────────────────────────
        csv_card = ctk.CTkFrame(
            panels, fg_color="#16213e", corner_radius=10
        )
        csv_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        csv_card.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            csv_card, text="Export CSV",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))

        ctk.CTkLabel(
            csv_card,
            text="Compatible Excel et Google Sheets.\nOuvre directement dans un tableur.",
            font=ctk.CTkFont(size=11), text_color="gray",
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

        self.csv_feedback = ctk.CTkLabel(
            csv_card, text="",
            font=ctk.CTkFont(size=11),
        )
        self.csv_feedback.grid(
            row=2, column=0, sticky="w", padx=16, pady=(0, 4)
        )

        ctk.CTkButton(
            csv_card, text="Télécharger .csv",
            height=38, fg_color="#1D9E75",
            hover_color="#0F6E56",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._export_csv,
        ).grid(row=3, column=0, sticky="ew",
               padx=16, pady=(0, 16))

        # ── Panneau PDF ───────────────────────────────────────
        pdf_card = ctk.CTkFrame(
            panels, fg_color="#16213e", corner_radius=10
        )
        pdf_card.grid(row=0, column=1, sticky="nsew")
        pdf_card.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            pdf_card, text="Relevé PDF",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))

        ctk.CTkLabel(
            pdf_card,
            text="Relevé mis en page avec tableau\net totaux. Prêt à partager.",
            font=ctk.CTkFont(size=11), text_color="gray",
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

        self.pdf_feedback = ctk.CTkLabel(
            pdf_card, text="",
            font=ctk.CTkFont(size=11),
        )
        self.pdf_feedback.grid(
            row=2, column=0, sticky="w", padx=16, pady=(0, 4)
        )

        ctk.CTkButton(
            pdf_card, text="Générer PDF",
            height=38, fg_color="#534AB7",
            hover_color="#3C3489",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._export_pdf,
        ).grid(row=3, column=0, sticky="ew",
               padx=16, pady=(0, 16))
        from ui.onboarding import show_onboarding
        show_onboarding(self, "exporter")

    def _get_transactions(self):
        period = self.period_var.get()
        month  = None if period == "Toutes les transactions" else period
        return get_transactions(state.current_user_id, month=month)

    def _export_csv(self):
        transactions = self._get_transactions()
        if not transactions:
            self.csv_feedback.configure(
                text="Aucune transaction à exporter.",
                text_color="#E24B4A"
            )
            return

        period   = self.period_var.get()
        default  = f"etubudget_{period.replace(' ', '_')}.csv"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichier CSV", "*.csv")],
            initialfile=default,
            title="Enregistrer le fichier CSV",
        )
        if not filepath:
            return

        ok = export_to_csv(transactions, filepath)
        if ok:
            self.csv_feedback.configure(
                text=f"Fichier créé !\n{os.path.basename(filepath)}",
                text_color="#5DCAA5"
            )
            self._open_file(filepath)
        else:
            self.csv_feedback.configure(
                text="Erreur lors de la création du fichier.",
                text_color="#E24B4A"
            )

    def _export_pdf(self):
        transactions = self._get_transactions()
        if not transactions:
            self.pdf_feedback.configure(
                text="Aucune transaction à exporter.",
                text_color="#E24B4A"
            )
            return

        period   = self.period_var.get()
        default  = f"etubudget_releve_{period.replace(' ', '_')}.pdf"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Fichier PDF", "*.pdf")],
            initialfile=default,
            title="Enregistrer le relevé PDF",
        )
        if not filepath:
            return

        ok = export_to_pdf(
            transactions,
            month=period,
            username=state.current_username,
            filepath=filepath,
        )
        if ok:
            self.pdf_feedback.configure(
                text=f"PDF généré !\n{os.path.basename(filepath)}",
                text_color="#5DCAA5"
            )
            self._open_file(filepath)
        else:
            self.pdf_feedback.configure(
                text="Erreur lors de la génération du PDF.",
                text_color="#E24B4A"
            )

    def _open_file(self, filepath):
        try:
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.run(["open", filepath])
            else:
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            print(f"Impossible d'ouvrir le fichier : {e}")

    def refresh(self):
        pass