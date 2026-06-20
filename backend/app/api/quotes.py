from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.bond import Bond, MarketSource
from app.models.quote import Quote
from app.schemas.quote import QuoteOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/quotes", tags=["报价"])


@router.get("/latest", response_model=list[QuoteOut])
async def get_latest_quotes(
    source_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = (
        select(Quote, MarketSource.name, MarketSource.source_type)
        .join(MarketSource, Quote.source_id == MarketSource.id)
    )
    if source_type:
        query = query.where(MarketSource.source_type == source_type)

    query = query.order_by(Quote.quote_time.desc()).limit(limit)
    result = await db.execute(query)
    rows = result.all()

    return [
        QuoteOut(
            **{c.key: getattr(q, c.key) for c in Quote.__table__.columns},
            source_name=sname,
            source_type=stype,
        )
        for q, sname, stype in rows
    ]


@router.get("/best")
async def get_best_quotes(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    subq = (
        select(
            Quote.bond_id,
            func.max(Quote.bid_price).label("best_bid"),
            func.min(Quote.ask_price).label("best_ask"),
            func.count(Quote.id).label("quote_count"),
        )
        .group_by(Quote.bond_id)
        .subquery()
    )

    result = await db.execute(
        select(Bond.id, Bond.code, Bond.name, Bond.bond_type, Bond.coupon_rate, Bond.remaining_term,
               subq.c.best_bid, subq.c.best_ask, subq.c.quote_count)
        .join(subq, Bond.id == subq.c.bond_id)
        .order_by(subq.c.quote_count.desc())
        .limit(limit)
    )

    rows = result.all()
    return [
        {
            "bond_id": str(row.id),
            "code": row.code,
            "name": row.name,
            "bond_type": row.bond_type,
            "coupon_rate": float(row.coupon_rate) if row.coupon_rate else None,
            "remaining_term": float(row.remaining_term) if row.remaining_term else None,
            "best_bid": float(row.best_bid) if row.best_bid else None,
            "best_ask": float(row.best_ask) if row.best_ask else None,
            "spread": round(float(row.best_ask) - float(row.best_bid), 4) if row.best_ask and row.best_bid else None,
            "quote_count": row.quote_count,
        }
        for row in rows
    ]


@router.get("/matrix")
async def get_quote_matrix(
    source_type: Optional[str] = Query("broker", description="行情源类型"),
    bond_limit: int = Query(15, ge=5, le=50, description="债券数量"),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    sources_query = (
        select(MarketSource.id, MarketSource.name, MarketSource.source_type)
        .where(MarketSource.is_enabled == True)
    )
    if source_type:
        sources_query = sources_query.where(MarketSource.source_type == source_type)
    sources_query = sources_query.order_by(MarketSource.name)

    sources_result = await db.execute(sources_query)
    sources = sources_result.all()
    source_ids = [s.id for s in sources]

    bond_count_subq = (
        select(
            Quote.bond_id,
            func.count(distinct(Quote.source_id)).label("source_count"),
            func.count(Quote.id).label("quote_count"),
        )
        .where(Quote.source_id.in_(source_ids))
        .group_by(Quote.bond_id)
        .subquery()
    )

    bonds_result = await db.execute(
        select(
            Bond.id, Bond.code, Bond.name, Bond.bond_type,
            Bond.coupon_rate, Bond.remaining_term, Bond.credit_rating,
            bond_count_subq.c.source_count, bond_count_subq.c.quote_count
        )
        .join(bond_count_subq, Bond.id == bond_count_subq.c.bond_id)
        .order_by(bond_count_subq.c.quote_count.desc())
        .limit(bond_limit)
    )
    bonds = bonds_result.all()
    bond_ids = [b.id for b in bonds]

    latest_quotes_subq = (
        select(
            Quote.bond_id,
            Quote.source_id,
            Quote.bid_price,
            Quote.ask_price,
            Quote.bid_yield,
            Quote.ask_yield,
            Quote.quote_time,
            func.row_number().over(
                partition_by=(Quote.bond_id, Quote.source_id),
                order_by=Quote.quote_time.desc()
            ).label("rn")
        )
        .where(Quote.bond_id.in_(bond_ids))
        .where(Quote.source_id.in_(source_ids))
        .subquery()
    )

    quotes_result = await db.execute(
        select(latest_quotes_subq)
        .where(latest_quotes_subq.c.rn == 1)
    )
    quote_rows = quotes_result.all()

    quote_map = {}
    for q in quote_rows:
        key = (str(q.bond_id), str(q.source_id))
        quote_map[key] = {
            "bid_price": float(q.bid_price) if q.bid_price else None,
            "ask_price": float(q.ask_price) if q.ask_price else None,
            "bid_yield": float(q.bid_yield) if q.bid_yield else None,
            "ask_yield": float(q.ask_yield) if q.ask_yield else None,
            "quote_time": q.quote_time.isoformat() if q.quote_time else None,
        }

    bond_list = [
        {
            "bond_id": str(b.id),
            "code": b.code,
            "name": b.name,
            "bond_type": b.bond_type,
            "coupon_rate": float(b.coupon_rate) if b.coupon_rate else None,
            "remaining_term": float(b.remaining_term) if b.remaining_term else None,
            "credit_rating": b.credit_rating,
        }
        for b in bonds
    ]

    source_list = [
        {
            "source_id": str(s.id),
            "name": s.name,
            "source_type": s.source_type,
        }
        for s in sources
    ]

    matrix = []
    for bond in bond_list:
        row = {"bond": bond, "quotes": {}}
        for source in source_list:
            key = (bond["bond_id"], source["source_id"])
            row["quotes"][source["source_id"]] = quote_map.get(key)
        matrix.append(row)

    return {
        "bonds": bond_list,
        "sources": source_list,
        "matrix": matrix,
    }
