from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.bond import Bond, MarketSource
from app.models.quote import Quote
from app.models.trade import Trade
from app.models.futures import FuturesQuote
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["看板"])


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    bond_count = await db.execute(select(func.count(Bond.id)))
    source_count = await db.execute(
        select(func.count(MarketSource.id)).where(MarketSource.status == "online")
    )
    quote_count = await db.execute(select(func.count(Quote.id)))
    trade_count = await db.execute(select(func.count(Trade.id)))
    trade_volume = await db.execute(select(func.sum(Trade.volume)))
    trade_amount = await db.execute(select(func.sum(Trade.amount)))

    return {
        "bond_count": bond_count.scalar() or 0,
        "online_source_count": source_count.scalar() or 0,
        "total_quotes": quote_count.scalar() or 0,
        "total_trades": trade_count.scalar() or 0,
        "total_volume": float(trade_volume.scalar() or 0),
        "total_amount": float(trade_amount.scalar() or 0),
    }


@router.get("/yield-curve")
async def get_yield_curve(db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    result = await db.execute(
        select(Bond.remaining_term, func.avg(Quote.bid_yield).label("avg_yield"))
        .join(Quote, Bond.id == Quote.bond_id)
        .where(Bond.bond_type == "国债")
        .where(Bond.remaining_term.isnot(None))
        .where(Quote.bid_yield.isnot(None))
        .group_by(Bond.remaining_term)
        .order_by(Bond.remaining_term)
    )
    rows = result.all()
    return [
        {"term": float(r.remaining_term), "yield": round(float(r.avg_yield), 4)}
        for r in rows
    ]


@router.get("/hot-bonds")
async def get_hot_bonds(db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    result = await db.execute(
        select(
            Bond.id, Bond.code, Bond.name, Bond.bond_type,
            func.sum(Trade.volume).label("total_vol"),
            func.sum(Trade.amount).label("total_amt"),
            func.count(Trade.id).label("trade_cnt"),
        )
        .join(Trade, Bond.id == Trade.bond_id)
        .group_by(Bond.id, Bond.code, Bond.name, Bond.bond_type)
        .order_by(desc("total_vol"))
        .limit(10)
    )
    rows = result.all()
    return [
        {
            "bond_id": str(r.id),
            "code": r.code,
            "name": r.name,
            "bond_type": r.bond_type,
            "total_volume": float(r.total_vol or 0),
            "total_amount": float(r.total_amt or 0),
            "trade_count": r.trade_cnt,
        }
        for r in rows
    ]


@router.get("/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    result = await db.execute(
        select(
            Bond.id, Bond.code, Bond.name,
            func.max(Quote.bid_price).label("max_bid"),
            func.min(Quote.ask_price).label("min_ask"),
            func.max(Quote.bid_yield).label("max_yield"),
            func.min(Quote.ask_yield).label("min_yield"),
        )
        .join(Quote, Bond.id == Quote.bond_id)
        .group_by(Bond.id, Bond.code, Bond.name)
        .limit(15)
    )
    rows = result.all()
    alerts = []
    for r in rows:
        if r.max_bid and r.min_ask:
            spread = float(r.max_bid) - float(r.min_ask)
            if abs(spread) > 0.2:
                alerts.append({
                    "bond_id": str(r.id),
                    "code": r.code,
                    "name": r.name,
                    "type": "price_spread",
                    "message": f"买卖价差异常: {spread:.4f}",
                    "level": "warning" if abs(spread) < 0.5 else "danger",
                })
        if r.max_yield and r.min_yield:
            yield_spread = float(r.max_yield) - float(r.min_yield)
            if yield_spread > 0.1:
                alerts.append({
                    "bond_id": str(r.id),
                    "code": r.code,
                    "name": r.name,
                    "type": "yield_spread",
                    "message": f"收益率差异较大: {yield_spread:.4f}%",
                    "level": "info",
                })
    return alerts


@router.get("/heatmap")
async def get_heatmap_data(db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    term_buckets = [
        (0, 1, "1年以内"),
        (1, 3, "1-3年"),
        (3, 5, "3-5年"),
        (5, 10, "5-10年"),
        (10, 999, "10年以上"),
    ]

    bond_types = ["国债", "政金债", "企业债", "公司债", "可转债", "地方债", "同业存单"]

    term_case = case(
        *[
            (and_(Bond.remaining_term >= start, Bond.remaining_term < end), label)
            for start, end, label in term_buckets
        ],
        else_=None
    ).label("term_bucket")

    price_change = func.avg((Trade.price - Bond.face_value) / Bond.face_value * 100).label("avg_change")
    total_volume = func.sum(Trade.volume).label("total_volume")
    trade_count = func.count(Trade.id).label("trade_count")

    query = (
        select(
            Bond.bond_type,
            term_case,
            price_change,
            total_volume,
            trade_count,
        )
        .select_from(Bond)
        .join(Trade, Bond.id == Trade.bond_id)
        .where(Bond.bond_type.in_(bond_types))
        .where(Bond.remaining_term.isnot(None))
        .where(Trade.price.isnot(None))
        .where(Bond.face_value.isnot(None))
        .group_by(Bond.bond_type, term_case)
    )

    result = await db.execute(query)
    rows = result.all()

    data_map = {}
    for row in rows:
        if row.term_bucket:
            key = f"{row.bond_type}|{row.term_bucket}"
            data_map[key] = {
                "bond_type": row.bond_type,
                "term_bucket": row.term_bucket,
                "avg_change": round(float(row.avg_change or 0), 4),
                "total_volume": float(row.total_volume or 0),
                "trade_count": row.trade_count or 0,
            }

    heatmap_data = []
    for bond_type in bond_types:
        for _, _, term_label in term_buckets:
            key = f"{bond_type}|{term_label}"
            cell = data_map.get(key, {
                "bond_type": bond_type,
                "term_bucket": term_label,
                "avg_change": 0,
                "total_volume": 0,
                "trade_count": 0,
            })
            heatmap_data.append(cell)

    return {
        "term_buckets": [label for _, _, label in term_buckets],
        "bond_types": bond_types,
        "data": heatmap_data,
    }
