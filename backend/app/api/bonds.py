from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.bond import BondOut, BondListOut
from app.schemas.quote import QuoteOut, AggregatedQuoteOut
from app.schemas.trade import TradeOut
from app.api.deps import get_current_user
from app.services import market_data

router = APIRouter(prefix="/api/bonds", tags=["债券"])


@router.get("", response_model=BondListOut)
async def list_bonds(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    bond_type: Optional[str] = Query(None, description="债券类型"),
    credit_rating: Optional[str] = Query(None, description="信用评级"),
    term_min: Optional[float] = Query(None, description="剩余期限最小值(年)"),
    term_max: Optional[float] = Query(None, description="剩余期限最大值(年)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await market_data.list_bonds(
        db,
        keyword=keyword,
        bond_type=bond_type,
        credit_rating=credit_rating,
        term_min=term_min,
        term_max=term_max,
        page=page,
        page_size=page_size,
    )


@router.get("/{bond_id}", response_model=BondOut)
async def get_bond(bond_id: UUID, db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    bond = await market_data.get_bond_by_id(db, bond_id)
    if not bond:
        raise HTTPException(status_code=404, detail="债券不存在")
    return BondOut.model_validate(bond)


@router.get("/{bond_id}/quotes", response_model=list[QuoteOut])
async def get_bond_quotes(bond_id: UUID, db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    return await market_data.get_bond_quotes(db, bond_id)


@router.get("/{bond_id}/trades", response_model=list[TradeOut])
async def get_bond_trades(bond_id: UUID, db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    return await market_data.get_bond_trades(db, bond_id)


@router.get("/{bond_id}/aggregated", response_model=AggregatedQuoteOut)
async def get_aggregated_quotes(bond_id: UUID, db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    result = await market_data.get_aggregated_quotes(db, bond_id)
    if not result:
        raise HTTPException(status_code=404, detail="债券不存在")
    return result
