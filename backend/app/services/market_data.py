from typing import Optional, Tuple, Any
from uuid import UUID

from sqlalchemy import select, func, or_, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bond import Bond, MarketSource
from app.models.quote import Quote
from app.models.trade import Trade
from app.schemas.bond import BondOut, BondListOut
from app.schemas.quote import QuoteOut, AggregatedQuoteOut, SourceQuoteSummary, BondBasic
from app.schemas.trade import TradeOut, TradeListOut, TradeStatistics


def _map_row_to_quote_out(row: Any) -> QuoteOut:
    q, sname, stype = row
    return QuoteOut(
        **{c.key: getattr(q, c.key) for c in Quote.__table__.columns},
        source_name=sname,
        source_type=stype,
    )


def _map_row_to_trade_out(row: Any) -> TradeOut:
    t, sname, stype, bcode, bname = row
    return TradeOut(
        **{c.key: getattr(t, c.key) for c in Trade.__table__.columns},
        source_name=sname,
        source_type=stype,
        bond_code=bcode,
        bond_name=bname,
    )


async def _paginate_query(
    db: AsyncSession,
    query,
    count_query,
    page: int,
    page_size: int,
    order_by=None,
    use_scalars: bool = False,
) -> Tuple[list, int]:
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    if order_by is not None:
        query = query.order_by(order_by)
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    if use_scalars:
        items = result.scalars().all()
    else:
        items = result.all()

    return items, total


async def list_bonds(
    db: AsyncSession,
    keyword: Optional[str] = None,
    bond_type: Optional[str] = None,
    credit_rating: Optional[str] = None,
    term_min: Optional[float] = None,
    term_max: Optional[float] = None,
    page: int = 1,
    page_size: int = 20,
) -> BondListOut:
    query = select(Bond)
    count_query = select(func.count(Bond.id))

    if keyword:
        kw = f"%{keyword}%"
        filter_cond = or_(Bond.code.ilike(kw), Bond.name.ilike(kw), Bond.issuer.ilike(kw))
        query = query.where(filter_cond)
        count_query = count_query.where(filter_cond)

    if bond_type:
        query = query.where(Bond.bond_type == bond_type)
        count_query = count_query.where(Bond.bond_type == bond_type)

    if credit_rating:
        query = query.where(Bond.credit_rating == credit_rating)
        count_query = count_query.where(Bond.credit_rating == credit_rating)

    if term_min is not None:
        query = query.where(Bond.remaining_term >= term_min)
        count_query = count_query.where(Bond.remaining_term >= term_min)

    if term_max is not None:
        query = query.where(Bond.remaining_term < term_max)
        count_query = count_query.where(Bond.remaining_term < term_max)

    bonds, total = await _paginate_query(
        db, query, count_query, page, page_size, order_by=Bond.code, use_scalars=True
    )

    return BondListOut(
        items=[BondOut.model_validate(b) for b in bonds],
        total=total,
        page=page,
        page_size=page_size,
    )


async def get_bond_by_id(db: AsyncSession, bond_id: UUID) -> Optional[Bond]:
    result = await db.execute(select(Bond).where(Bond.id == bond_id))
    return result.scalar_one_or_none()


async def get_bond_quotes(
    db: AsyncSession,
    bond_id: UUID,
    limit: int = 100,
) -> list[QuoteOut]:
    result = await db.execute(
        select(Quote, MarketSource.name, MarketSource.source_type)
        .join(MarketSource, Quote.source_id == MarketSource.id)
        .where(Quote.bond_id == bond_id)
        .order_by(Quote.quote_time.desc())
        .limit(limit)
    )
    rows = result.all()
    return [_map_row_to_quote_out(row) for row in rows]


async def get_bond_trades(
    db: AsyncSession,
    bond_id: UUID,
    limit: int = 100,
) -> list[TradeOut]:
    result = await db.execute(
        select(Trade, MarketSource.name, MarketSource.source_type, Bond.code, Bond.name.label("bname"))
        .join(MarketSource, Trade.source_id == MarketSource.id)
        .join(Bond, Trade.bond_id == Bond.id)
        .where(Trade.bond_id == bond_id)
        .order_by(Trade.trade_time.desc())
        .limit(limit)
    )
    rows = result.all()
    return [_map_row_to_trade_out(row) for row in rows]


async def get_aggregated_quotes(
    db: AsyncSession,
    bond_id: UUID,
) -> Optional[AggregatedQuoteOut]:
    bond = await get_bond_by_id(db, bond_id)
    if not bond:
        return None

    quotes_result = await db.execute(
        select(
            MarketSource.name,
            MarketSource.source_type,
            func.max(Quote.bid_price).label("best_bid"),
            func.min(Quote.ask_price).label("best_ask"),
            func.max(Quote.bid_yield).label("best_bid_yield"),
            func.min(Quote.ask_yield).label("best_ask_yield"),
            func.count(Quote.id).label("cnt"),
            func.max(Quote.quote_time).label("latest_time"),
        )
        .join(MarketSource, Quote.source_id == MarketSource.id)
        .where(Quote.bond_id == bond_id)
        .group_by(MarketSource.name, MarketSource.source_type)
    )
    source_rows = quotes_result.all()

    sources = []
    global_best_bid = None
    global_best_ask = None
    global_best_bid_yield = None
    global_best_ask_yield = None
    total_quotes = 0

    for row in source_rows:
        sources.append(SourceQuoteSummary(
            source_name=row.name,
            source_type=row.source_type,
            best_bid_price=float(row.best_bid) if row.best_bid else None,
            best_ask_price=float(row.best_ask) if row.best_ask else None,
            best_bid_yield=float(row.best_bid_yield) if row.best_bid_yield else None,
            best_ask_yield=float(row.best_ask_yield) if row.best_ask_yield else None,
            quote_count=row.cnt,
            latest_quote_time=row.latest_time,
        ))
        total_quotes += row.cnt

        if row.best_bid and (global_best_bid is None or float(row.best_bid) > global_best_bid):
            global_best_bid = float(row.best_bid)
        if row.best_ask and (global_best_ask is None or float(row.best_ask) < global_best_ask):
            global_best_ask = float(row.best_ask)
        if row.best_bid_yield and (global_best_bid_yield is None or float(row.best_bid_yield) > global_best_bid_yield):
            global_best_bid_yield = float(row.best_bid_yield)
        if row.best_ask_yield and (global_best_ask_yield is None or float(row.best_ask_yield) < global_best_ask_yield):
            global_best_ask_yield = float(row.best_ask_yield)

    spread = None
    if global_best_ask and global_best_bid:
        spread = round(global_best_ask - global_best_bid, 4)

    return AggregatedQuoteOut(
        bond=BondBasic.model_validate(bond),
        sources=sources,
        best_bid_price=global_best_bid,
        best_ask_price=global_best_ask,
        best_bid_yield=global_best_bid_yield,
        best_ask_yield=global_best_ask_yield,
        spread=spread,
        total_quotes=total_quotes,
    )


async def get_latest_quotes(
    db: AsyncSession,
    source_type: Optional[str] = None,
    limit: int = 50,
) -> list[QuoteOut]:
    query = (
        select(Quote, MarketSource.name, MarketSource.source_type)
        .join(MarketSource, Quote.source_id == MarketSource.id)
    )
    if source_type:
        query = query.where(MarketSource.source_type == source_type)

    query = query.order_by(Quote.quote_time.desc()).limit(limit)
    result = await db.execute(query)
    rows = result.all()

    return [_map_row_to_quote_out(row) for row in rows]


async def get_best_quotes(
    db: AsyncSession,
    limit: int = 20,
) -> list[dict]:
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


async def get_quote_matrix(
    db: AsyncSession,
    source_type: Optional[str] = "broker",
    bond_limit: int = 15,
) -> dict:
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


async def get_recent_trades(
    db: AsyncSession,
    source_type: Optional[str] = None,
    bond_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 30,
) -> TradeListOut:
    query = (
        select(Trade, MarketSource.name, MarketSource.source_type, Bond.code, Bond.name.label("bname"))
        .join(MarketSource, Trade.source_id == MarketSource.id)
        .join(Bond, Trade.bond_id == Bond.id)
    )
    count_query = select(func.count(Trade.id)).select_from(Trade)

    if source_type:
        query = query.where(MarketSource.source_type == source_type)
        count_query = count_query.join(MarketSource, Trade.source_id == MarketSource.id).where(
            MarketSource.source_type == source_type
        )
    if bond_type:
        query = query.where(Bond.bond_type == bond_type)
        count_query = count_query.join(Bond, Trade.bond_id == Bond.id).where(Bond.bond_type == bond_type)

    trade_rows, total = await _paginate_query(
        db, query, count_query, page, page_size, order_by=Trade.trade_time.desc()
    )

    items = [_map_row_to_trade_out(row) for row in trade_rows]

    return TradeListOut(items=items, total=total, page=page, page_size=page_size)


async def get_trade_statistics(db: AsyncSession) -> TradeStatistics:
    stats_result = await db.execute(
        select(
            func.sum(Trade.volume).label("total_vol"),
            func.sum(Trade.amount).label("total_amt"),
            func.count(Trade.id).label("cnt"),
            func.avg(Trade.price).label("avg_p"),
            func.avg(Trade.yield_rate).label("avg_y"),
        )
    )
    stats = stats_result.one()

    by_source_result = await db.execute(
        select(
            MarketSource.name,
            MarketSource.source_type,
            func.sum(Trade.volume).label("vol"),
            func.sum(Trade.amount).label("amt"),
            func.count(Trade.id).label("cnt"),
        )
        .join(MarketSource, Trade.source_id == MarketSource.id)
        .group_by(MarketSource.name, MarketSource.source_type)
    )

    by_type_result = await db.execute(
        select(
            Bond.bond_type,
            func.sum(Trade.volume).label("vol"),
            func.sum(Trade.amount).label("amt"),
            func.count(Trade.id).label("cnt"),
        )
        .join(Bond, Trade.bond_id == Bond.id)
        .group_by(Bond.bond_type)
    )

    return TradeStatistics(
        total_volume=float(stats.total_vol or 0),
        total_amount=float(stats.total_amt or 0),
        trade_count=stats.cnt or 0,
        avg_price=round(float(stats.avg_p), 4) if stats.avg_p else None,
        avg_yield=round(float(stats.avg_y), 4) if stats.avg_y else None,
        by_source=[
            {"name": r.name, "type": r.source_type, "volume": float(r.vol or 0),
             "amount": float(r.amt or 0), "count": r.cnt}
            for r in by_source_result.all()
        ],
        by_bond_type=[
            {"bond_type": r.bond_type, "volume": float(r.vol or 0),
             "amount": float(r.amt or 0), "count": r.cnt}
            for r in by_type_result.all()
        ],
    )
