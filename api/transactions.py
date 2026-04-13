from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from api.deps import get_current_user
from database.queries import (
    get_transactions,
    insert_transaction,
    update_transaction,
    delete_transaction,
    get_available_months,
    get_last_transactions,
)
from utils.validators import validate_transaction_fields

router = APIRouter(prefix="/transactions", tags=["transactions"])


# ── Modèles ───────────────────────────────────────────────────────────────────
class TransactionCreate(BaseModel):
    amount:      str
    description: Optional[str] = ""
    date:        str
    tx_type:     str
    category_id: Optional[int] = None


class TransactionUpdate(BaseModel):
    amount:      str
    description: Optional[str] = ""
    date:        str
    tx_type:     str
    category_id: Optional[int] = None


# ── Routes ────────────────────────────────────────────────────────────────────
@router.get("/")
async def list_transactions(
    month:       Optional[str] = None,
    category_id: Optional[int] = None,
    tx_type:     Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Retourne les transactions avec filtres optionnels."""
    return get_transactions(
        current_user["id"],
        month=month,
        category_id=category_id,
        tx_type=tx_type,
    )


@router.get("/last")
async def last_transactions(
    limit: int = 5,
    current_user: dict = Depends(get_current_user),
):
    """Retourne les N dernières transactions."""
    return get_last_transactions(current_user["id"], limit=limit)


@router.get("/months")
async def available_months(
    current_user: dict = Depends(get_current_user),
):
    """Retourne les mois disponibles."""
    return get_available_months(current_user["id"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    current_user: dict = Depends(get_current_user),
):
    """Crée une nouvelle transaction."""
    ok, msg, amount, date_iso = validate_transaction_fields(
        data.amount, data.date
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    success = insert_transaction(
        user_id=current_user["id"],
        amount=amount,
        description=data.description or "",
        date=date_iso,
        tx_type=data.tx_type,
        category_id=data.category_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la creation de la transaction"
        )
    return {"message": "Transaction creee avec succes"}


@router.put("/{tx_id}")
async def edit_transaction(
    tx_id: int,
    data:  TransactionUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Modifie une transaction existante."""
    ok, msg, amount, date_iso = validate_transaction_fields(
        data.amount, data.date
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    success = update_transaction(
        tx_id=tx_id,
        user_id=current_user["id"],
        amount=amount,
        description=data.description or "",
        date=date_iso,
        tx_type=data.tx_type,
        category_id=data.category_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction introuvable ou non autorisee"
        )
    return {"message": "Transaction mise a jour"}


@router.delete("/{tx_id}")
async def remove_transaction(
    tx_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Supprime une transaction."""
    success = delete_transaction(tx_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction introuvable ou non autorisee"
        )
    return {"message": "Transaction supprimee"}