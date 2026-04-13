from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from api.auth         import router as auth_router
from api.transactions import router as transactions_router
from api.categories   import router as categories_router
from api.stats        import router as stats_router
from database.models  import create_tables

create_tables()

app = FastAPI(
    title="EtuBudget API",
    description="API du tracker de dépenses pour étudiants",
    version="2.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(stats_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/auth/login")

@app.get("/auth/login", response_class=HTMLResponse)
async def auth_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/add", response_class=HTMLResponse)
async def add(request: Request):
    return templates.TemplateResponse(request=request, name="add.html")

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    return templates.TemplateResponse(request=request, name="history.html")

@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    return templates.TemplateResponse(request=request, name="stats.html")

@app.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request):
    return templates.TemplateResponse(request=request, name="categories.html")

@app.get("/export", response_class=HTMLResponse)
async def export_page(request: Request):
    return templates.TemplateResponse(request=request, name="export.html")