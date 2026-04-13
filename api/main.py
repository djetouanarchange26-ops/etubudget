from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.auth         import router as auth_router
from api.transactions import router as transactions_router
from api.categories   import router as categories_router
from api.stats        import router as stats_router
from database.models  import create_tables

# Créer les tables au démarrage si elles n'existent pas
create_tables()

app = FastAPI(
    title="EtuBudget API",
    description="API du tracker de dépenses pour étudiants",
    version="2.0.0",
)

# Fichiers statiques (CSS, JS, icônes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routes
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(stats_router)


@app.get("/")
async def root():
    return {"message": "EtuBudget API v2.0 — /docs pour la documentation"}