from fastapi import APIRouter, Depends
from typing import Optional

from api.deps import get_current_user
from database.queries import (
    get_monthly_summary,
    get_daily_spending,
    get_spending_by_category,
    get_total_balance,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary")
async def monthly_summary(
    month: str,
    current_user: dict = Depends(get_current_user),
):
    """Résumé mensuel : dépenses, revenus, solde, nb transactions."""
    return get_monthly_summary(current_user["id"], month)


@router.get("/balance")
async def total_balance(
    current_user: dict = Depends(get_current_user),
):
    """Solde cumulé depuis le début."""
    balance = get_total_balance(current_user["id"])
    return {"balance": balance}


@router.get("/daily")
async def daily_spending(
    month: str,
    current_user: dict = Depends(get_current_user),
):
    """Dépenses par jour pour un mois donné."""
    return get_daily_spending(current_user["id"], month)


@router.get("/by-category")
async def spending_by_category(
    month: str,
    current_user: dict = Depends(get_current_user),
):
    """Dépenses réparties par catégorie pour un mois donné."""
    return get_spending_by_category(current_user["id"], month)