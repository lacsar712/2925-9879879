from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.trade import TradeListOut, TradeStatistics
from app.api.deps import get_current_user
from app.services import market_data

router = APIRouter(prefix="/api/trades", tags=["成交"])


@router.get("/recent", response_model=TradeListOut)
async def get_recent_trades(
    source_type: Optional[str] = Query(None),
    bond_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await market_data.get_recent_trades(
        db,
        source_type=source_type,
        bond_type=bond_type,
        page=page,
        page_size=page_size,
    )


@router.get("/statistics", response_model=TradeStatistics)
async def get_trade_statistics(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await market_data.get_trade_statistics(db)
