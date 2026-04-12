import csv
import os
from fpdf import FPDF


def export_to_csv(transactions, filepath):
    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Date", "Categorie", "Description", "Montant", "Type"])
            for tx in transactions:
                writer.writerow([
                    tx.get("date", ""),
                    tx.get("category_name") or "Sans categorie",
                    tx.get("description")   or "",
                    f"{tx['amount']:.2f}",
                    tx.get("type", ""),
                ])
        return True
    except Exception as e:
        print(f"Erreur export CSV : {e}")
        return False


class RelevePDF(FPDF):
    def __init__(self, username, month):
        super().__init__()
        self.username = username
        self.month    = month

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(15, 110, 86)
        self.cell(0, 10, "EtuBudget", ln=False)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10,
                  f"Releve de {self.username} - {self.month}",
                  align="R", ln=True)
        self.set_draw_color(15, 110, 86)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def export_to_pdf(transactions, month, username, filepath):
    try:
        pdf = RelevePDF(username, month)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # ── En-tete du tableau ────────────────────────────────
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(22, 33, 62)
        pdf.set_text_color(255, 255, 255)

        col_widths = [28, 38, 72, 28, 24]
        headers    = ["Date", "Categorie", "Description", "Montant", "Type"]

        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=0, fill=True, align="C")
        pdf.ln()

        # ── Lignes transactions ───────────────────────────────
        pdf.set_font("Helvetica", "", 8)
        total_depenses = 0
        total_revenus  = 0

        for idx, tx in enumerate(transactions):
            if idx % 2 == 0:
                pdf.set_fill_color(240, 242, 245)
            else:
                pdf.set_fill_color(255, 255, 255)

            is_dep = tx.get("type") == "depense"

            if is_dep:
                total_depenses += tx["amount"]
            else:
                total_revenus  += tx["amount"]

            montant_txt = f"-{tx['amount']:.2f}" if is_dep else f"+{tx['amount']:.2f}"

            # Date
            pdf.set_text_color(50, 50, 50)
            pdf.cell(col_widths[0], 7,
                     tx.get("date", ""), border=0, fill=True)

            # Categorie
            cat = (tx.get("category_name") or "Divers")[:18]
            pdf.cell(col_widths[1], 7, cat, border=0, fill=True)

            # Description — retirer les caracteres speciaux
            desc = (tx.get("description") or "")[:38]
            desc = desc.encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(col_widths[2], 7, desc, border=0, fill=True)

            # Montant
            if is_dep:
                pdf.set_text_color(180, 60, 60)
            else:
                pdf.set_text_color(15, 110, 86)
            pdf.cell(col_widths[3], 7, montant_txt,
                     border=0, fill=True, align="R")

            # Type
            pdf.set_text_color(100, 100, 100)
            pdf.cell(col_widths[4], 7,
                     tx.get("type", ""), border=0, fill=True, align="C")
            pdf.ln()

        # ── Separateur ────────────────────────────────────────
        pdf.ln(4)
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

        # ── Resume ────────────────────────────────────────────
        solde = total_revenus - total_depenses

        pdf.set_font("Helvetica", "B", 10)

        pdf.set_text_color(50, 50, 50)
        pdf.cell(140, 7, "Total depenses :", align="R")
        pdf.set_text_color(180, 60, 60)
        pdf.cell(30, 7, f"-{total_depenses:.2f}", align="R", ln=True)

        pdf.set_text_color(50, 50, 50)
        pdf.cell(140, 7, "Total revenus :", align="R")
        pdf.set_text_color(15, 110, 86)
        pdf.cell(30, 7, f"+{total_revenus:.2f}", align="R", ln=True)

        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(140, 8, "Solde net :", align="R")
        if solde >= 0:
            pdf.set_text_color(15, 110, 86)
        else:
            pdf.set_text_color(180, 60, 60)
        pdf.cell(30, 8,
                 f"{'+' if solde >= 0 else ''}{solde:.2f}",
                 align="R", ln=True)

        pdf.output(filepath)
        return True

    except Exception as e:
        print(f"Erreur export PDF : {e}")
        return False