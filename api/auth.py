from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from database.queries import create_user, get_user_by_username, seed_default_categories
from utils.validators import hash_password, check_password, validate_login_fields
from api.deps import create_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginForm(BaseModel):
    username: str
    password: str


@router.get("/login")
async def login_page():
    """Redirige vers la page de login servie par main.py"""
    return RedirectResponse(url="/login-page")


@router.post("/login")
async def login(form: LoginForm):
    ok, msg = validate_login_fields(form.username, form.password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    user = get_user_by_username(form.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")

    if not check_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mot de passe incorrect")

    token = create_token(user["id"], user["username"])
    return {"access_token": token, "token_type": "bearer",
            "username": user["username"], "user_id": user["id"]}


@router.post("/register")
async def register(form: LoginForm):
    ok, msg = validate_login_fields(form.username, form.password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    ok, msg = create_user(form.username, hash_password(form.password))
    if not ok:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

    user = get_user_by_username(form.username)
    seed_default_categories(user["id"])

    token = create_token(user["id"], user["username"])
    return {"access_token": token, "token_type": "bearer",
            "username": user["username"], "user_id": user["id"]}