# EtuBudget 💸

> Tracker de dépenses personnel conçu pour les étudiants — gratuit, 
> 100% local, aucune inscription requise.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green)
![SQLite](https://img.shields.io/badge/DB-SQLite-lightgrey)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## Pourquoi EtuBudget ?

En tant qu'étudiant, il est difficile de garder un oeil sur ses dépenses 
entre le loyer, les courses, les sorties et les abonnements. EtuBudget 
te permet de tout suivre en quelques secondes, sans compte en ligne, 
sans pub, sans partage de données — tout reste sur ton ordinateur.

---

## Fonctionnalités

### Gestion des transactions
- Ajouter des dépenses et revenus en 3 clics
- Catégories personnalisables avec couleurs
- Description optionnelle, date modifiable
- Modification et suppression depuis l'historique

### Dashboard
- Solde cumulé total depuis le début
- Résumé mensuel : dépenses, revenus, solde net
- Liste des dernières transactions
- Sélecteur de mois pour explorer l'historique

### Historique
- Filtres par mois, catégorie et type
- Total des transactions filtrées
- Modification et suppression inline

### Statistiques
- Courbe des dépenses par jour
- Camembert de répartition par catégorie
- Chiffres clés : total dépensé, reçu, solde net

### Conversion de devises
- Taux de change en temps réel via ExchangeRate API
- Devises disponibles : EUR, USD, FCFA, GBP, CAD, CHF, MAD, DZD
- Cache local pour éviter les appels répétés

### Export
- Export CSV compatible Excel et Google Sheets
- Relevé PDF mis en page avec tableau et totaux
- Choix de la période à exporter

### Confort d'utilisation
- Multi-utilisateurs — chaque étudiant a ses propres données
- Onboarding contextuel au premier accès à chaque écran
- Raccourcis clavier : Ctrl+N (ajouter), Ctrl+H (historique), 
  Ctrl+S (stats), Ctrl+E (exporter), Ctrl+D (dashboard)
- Thème sombre par défaut
- 6 catégories par défaut à l'inscription

---

## Téléchargement

Télécharge la dernière version depuis la page 
[Releases](../../releases) — aucune installation requise.

| Plateforme | Fichier |
|------------|---------|
| Windows    | `EtuBudget-Windows.exe` |
| macOS      | `EtuBudget-Mac.app.zip` |

> **Note Windows** : Windows Defender peut afficher un avertissement 
> "application inconnue". Clique sur "Informations complémentaires" 
> puis "Exécuter quand même". C'est normal pour une app non signée.

> **Note macOS** : Fais clic droit sur l'app → Ouvrir → Ouvrir quand 
> même. Ou désactive temporairement Gatekeeper dans les préférences 
> système.

---

## Installation depuis le code source

```bash
# 1. Cloner le repo
git clone https://github.com/djetouanarchange26-ops/etubudget.git
cd etubudget

# 2. Créer et activer le venv
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API de conversion de devises
# Crée un fichier secrets.env à la racine :
# EXCHANGE_API_KEY=ta_clé_depuis_exchangerate-api.com

# 5. Lancer l'app
python main.py
```

---
---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Interface | CustomTkinter 5.x |
| Base de données | SQLite (stdlib Python) |
| Graphiques | Matplotlib + FigureCanvasTkAgg |
| Export PDF | fpdf2 |
| Devises | ExchangeRate API (gratuit) |
| Packaging | PyInstaller |
| CI/CD | GitHub Actions |

---

## Roadmap

- [x] MVP Desktop — CustomTkinter
- [ ] Budget par catégorie avec alertes
- [ ] Transactions récurrentes
- [ ] Objectifs d'épargne
- [ ] Version PWA mobile (FastAPI + HTML/CSS)
- [ ] Synchronisation cloud

---

## Contribuer

Les contributions sont les bienvenues ! Ouvre une issue ou une 
pull request.

---

## Licence

MIT — libre d'utilisation, modification et distribution.

---

*Fait avec Python par et pour des étudiants.*