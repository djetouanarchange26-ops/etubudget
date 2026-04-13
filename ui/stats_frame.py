import customtkinter as ctk
from datetime import datetime
import state
from utils.config import get_config
from utils.currency import convert
from database.queries import (
    get_monthly_summary,
    get_daily_spending,
    get_spending_by_category,
    get_available_months,
)

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False


class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current_month = datetime.now().strftime("%Y-%m")
        self._canvas_curve = None
        self._canvas_pie   = None
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        # ── En-tête ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        ctk.CTkLabel(
            header, text="Statistiques",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Visualise tes dépenses et revenus",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        # ── Sélecteur de mois ─────────────────────────────────
        month_row = ctk.CTkFrame(self, fg_color="transparent")
        month_row.grid(row=1, column=0, sticky="ew", padx=24, pady=(14, 0))

        ctk.CTkLabel(
            month_row, text="Mois :",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(side="left", padx=(0, 8))

        months = get_available_months(state.current_user_id)
        if not months:
            months = [self.current_month]
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

        # ── Chiffres clés ─────────────────────────────────────
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.grid(
            row=2, column=0, sticky="ew", padx=24, pady=(14, 0)
        )
        for i in range(3):
            self.summary_frame.columnconfigure(i, weight=1)

        # ── Zone graphiques ───────────────────────────────────
        graphs = ctk.CTkFrame(self, fg_color="transparent")
        graphs.grid(row=3, column=0, sticky="ew", padx=24, pady=(14, 0))
        graphs.columnconfigure(0, weight=2)
        graphs.columnconfigure(1, weight=1)

        # Courbe à gauche
        self.curve_frame = ctk.CTkFrame(
            graphs, fg_color="#16213e", corner_radius=10
        )
        self.curve_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(
            self.curve_frame,
            text="Dépenses par jour",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(12, 4))

        self.curve_container = ctk.CTkFrame(
            self.curve_frame, fg_color="transparent"
        )
        self.curve_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Camembert à droite
        self.pie_frame = ctk.CTkFrame(
            graphs, fg_color="#16213e", corner_radius=10
        )
        self.pie_frame.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            self.pie_frame,
            text="Répartition",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(12, 4))

        self.pie_container = ctk.CTkFrame(
            self.pie_frame, fg_color="transparent"
        )
        self.pie_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # ── Légende camembert ─────────────────────────────────
        self.legend_frame = ctk.CTkScrollableFrame(
            self, fg_color="#16213e", corner_radius=10, height=100
        )
        self.legend_frame.grid(
            row=4, column=0, sticky="ew", padx=24, pady=(10, 16)
        )

        self._refresh_all()
        from ui.onboarding import show_onboarding
        show_onboarding(self, "stats")

    def _get_fmt(self):
        config  = get_config()
        api_key = config.get("api_key", "")
        base    = config.get("devise_base", "EUR")
        cible   = config.get("devise", "EUR")
        symbole = config.get("symbole", "€")

        def fmt(amount):
            converted = convert(amount, base, cible) if api_key else amount
            return f"{converted:.2f} {symbole}"

        return fmt, symbole, base, cible, api_key

    def _build_summary(self):
        for w in self.summary_frame.winfo_children():
            w.destroy()

        fmt, symbole, base, cible, api_key = self._get_fmt()
        summary = get_monthly_summary(state.current_user_id, self.current_month)

        items = [
            ("Total dépensé",  fmt(summary["total_depenses"]), "#F09595"),
            ("Total reçu",     fmt(summary["total_revenus"]),  "#5DCAA5"),
            ("Solde net",
             f"{'+' if summary['solde'] >= 0 else ''}{fmt(summary['solde'])}",
             "#5DCAA5" if summary["solde"] >= 0 else "#F09595"),
        ]

        for i, (label, value, color) in enumerate(items):
            card = ctk.CTkFrame(
                self.summary_frame, fg_color="#16213e", corner_radius=10
            )
            card.grid(
                row=0, column=i,
                padx=(0, 8) if i < 2 else 0,
                sticky="ew",
            )
            ctk.CTkLabel(
                card, text=label,
                font=ctk.CTkFont(size=11), text_color="gray",
            ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))
            ctk.CTkLabel(
                card, text=value,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=color,
            ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

    def _build_curve(self):
        for w in self.curve_container.winfo_children():
            w.destroy()

        if not MATPLOTLIB_OK:
            ctk.CTkLabel(
                self.curve_container,
                text="matplotlib non installé\npip install matplotlib",
                text_color="gray",
            ).pack(pady=20)
            return

        data = get_daily_spending(state.current_user_id, self.current_month)

        fig, ax = plt.subplots(figsize=(5, 2.8))
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")

        if not data:
            ax.text(
                0.5, 0.5,
                "Aucune dépense ce mois\nAjoute des transactions pour voir tes stats",
                ha="center", va="center",
                color="#9090a8", fontsize=9,
                transform=ax.transAxes,
                multialignment="center",
            )
        else:
            fmt, symbole, base, cible, api_key = self._get_fmt()
            dates  = [d["date"].split("-")[2] for d in data]
            totaux = [
                convert(d["total"], base, cible) if api_key else d["total"]
                for d in data
            ]
            ax.plot(dates, totaux, color="#F09595", linewidth=2, marker="o",
                    markersize=4, markerfacecolor="#F09595")
            ax.fill_between(dates, totaux, alpha=0.15, color="#F09595")
            ax.tick_params(colors="#9090a8", labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor("#2a2a4a")

        fig.tight_layout(pad=1.0)

        if self._canvas_curve:
            self._canvas_curve.get_tk_widget().destroy()

        self._canvas_curve = FigureCanvasTkAgg(
            fig, master=self.curve_container
        )
        self._canvas_curve.draw()
        self._canvas_curve.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _build_pie(self):
        for w in self.pie_container.winfo_children():
            w.destroy()
        for w in self.legend_frame.winfo_children():
            w.destroy()

        if not MATPLOTLIB_OK:
            return

        data = get_spending_by_category(state.current_user_id, self.current_month)

        fig, ax = plt.subplots(figsize=(2.8, 2.8))
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")

        if not data:
            ax.text(
                    0.5, 0.5,
                    "Aucune dépense ce mois\nAjoute des transactions pour voir tes stats",
                    ha="center", va="center",
                    color="#9090a8", fontsize=9,
                    transform=ax.transAxes,
                    multialignment="center",
                )
            
        else:
            fmt, symbole, base, cible, api_key = self._get_fmt()
            labels  = [d["category_name"] for d in data]
            sizes   = [d["total"] for d in data]
            colors  = [d["color"] for d in data]

            wedges, _ = ax.pie(
                sizes,
                colors=colors,
                startangle=90,
                wedgeprops={"linewidth": 1.5, "edgecolor": "#16213e"},
            )
            ax.axis("equal")

            # Légende en bas
            for i, d in enumerate(data):
                row = ctk.CTkFrame(
                    self.legend_frame, fg_color="transparent"
                )
                row.pack(fill="x", pady=2)

                ctk.CTkLabel(
                    row, text="",
                    width=14, height=14,
                    fg_color=d["color"],
                    corner_radius=3,
                ).pack(side="left", padx=(8, 6))

                ctk.CTkLabel(
                    row,
                    text=d["category_name"],
                    font=ctk.CTkFont(size=11),
                    anchor="w",
                ).pack(side="left")

                montant = convert(d["total"], base, cible) if api_key else d["total"]
                ctk.CTkLabel(
                    row,
                    text=f"{d['percentage']}%  —  {montant:.2f} {symbole}",
                    font=ctk.CTkFont(size=11),
                    text_color="gray",
                ).pack(side="right", padx=8)

        fig.tight_layout(pad=0.5)

        if self._canvas_pie:
            self._canvas_pie.get_tk_widget().destroy()

        self._canvas_pie = FigureCanvasTkAgg(
            fig, master=self.pie_container
        )
        self._canvas_pie.draw()
        self._canvas_pie.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _refresh_all(self):
        self._build_summary()
        self._build_curve()
        self._build_pie()

    def _on_month_change(self, month):
        self.current_month = month
        self._refresh_all()

    def refresh(self):
        months = get_available_months(state.current_user_id)
        if not months:
            months = [self.current_month]
        if self.current_month not in months:
            months = [self.current_month] + months
        self.month_menu.configure(values=months)
        self._refresh_all()