from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.quote import QuoteOut
from app.api.deps import get_current_user
from app.services import market_data

router = APIRouter(prefix="/api/quotes", tags=["报价"])


@router.get("/latest", response_model=list[QuoteOut])
async def get_latest_quotes(
    source_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await market_data.get_latest_quotes(db, source_type=source_type, limit=limit)


@router.get("/best")
async def get_best_quotes(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await market_data.get_best_quotes(db, limit=limit)


@router.get("/matrix")
async def get_quote_matrix(
    source_type: Optional[str] = Query("broker", description="行情源类型"),
    bond_limit: int = Query(15, ge=5, le=50, description="债券数量"),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await market_data.get_quote_matrix(db, source_type=source_type, bond_limit=bond_limit)
