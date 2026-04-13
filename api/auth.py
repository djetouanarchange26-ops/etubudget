from fastapi import APIRouter, HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path

from database.queries import create_user, get_user_by_username, seed_default_categories
from utils.validators import hash_password, check_password, validate_login_fields
from api.deps import create_token

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")


# ── Modèles Pydantic ──────────────────────────────────────────────────────────
class LoginForm(BaseModel):
    username: str
    password: str


# ── Pages HTML ────────────────────────────────────────────────────────────────
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Affiche la page de login."""
    return templates.TemplateResponse("login.html", {"request": request})


# ── Routes API ────────────────────────────────────────────────────────────────
@router.post("/login")
async def login(form: LoginForm, response: Response):
    """Connecte un utilisateur et retourne un token JWT."""

    # 1. Validation des champs
    ok, msg = validate_login_fields(form.username, form.password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    # 2. Vérifier que l'utilisateur existe
    user = get_user_by_username(form.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable"
        )

    # 3. Vérifier le mot de passe
    if not check_password(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect"
        )

    # 4. Créer et retourner le token
    token = create_token(user["id"], user["username"])
    return {
        "access_token": token,
        "token_type":   "bearer",
        "username":     user["username"],
        "user_id":      user["id"],
    }


@router.post("/register")
async def register(form: LoginForm):
    """Crée un nouveau compte utilisateur."""

    # 1. Validation des champs
    ok, msg = validate_login_fields(form.username, form.password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    # 2. Créer l'utilisateur
    ok, msg = create_user(form.username, hash_password(form.password))
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg
        )

    # 3. Récupérer l'id et créer les catégories par défaut
    user = get_user_by_username(form.username)
    seed_default_categories(user["id"])

    # 4. Connecter automatiquement après inscription
    token = create_token(user["id"], user["username"])
    return {
        "access_token": token,
        "token_type":   "bearer",
        "username":     user["username"],
        "user_id":      user["id"],
    }