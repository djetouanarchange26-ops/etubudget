from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.deps import get_current_user
from database.queries import (
    get_categories_for_user,
    insert_category,
    delete_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    name:  str
    color: str


@router.get("/")
async def list_categories(
    current_user: dict = Depends(get_current_user),
):
    """Retourne toutes les categories de l'utilisateur."""
    return get_categories_for_user(current_user["id"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    current_user: dict = Depends(get_current_user),
):
    """Crée une nouvelle catégorie."""
    if not data.name or len(data.name.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom trop court — 2 caracteres minimum"
        )

    ok, msg = insert_category(current_user["id"], data.name, data.color)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg
        )
    return {"message": "Categorie creee"}


@router.delete("/{category_id}")
async def remove_category(
    category_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Supprime une catégorie."""
    ok, msg = delete_category(category_id, current_user["id"])
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg
        )
    return {"message": "Categorie supprimee"}