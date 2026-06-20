from datetime import date, timedelta
from typing import Optional
from calendar import monthrange

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_, and_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.bond import Bond
from app.schemas.calendar import BondCalendarEvent, CalendarDayEvents, CalendarMonthOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/calendar", tags=["债券日历"])


EVENT_TYPE_ISSUE = "issue"
EVENT_TYPE_MATURITY = "maturity"

EVENT_TITLES = {
    EVENT_TYPE_ISSUE: "新发债",
    EVENT_TYPE_MATURITY: "到期日",
}


def _create_event(bond: Bond, event_type: str, event_date: date) -> BondCalendarEvent:
    return BondCalendarEvent(
        id=bond.id,
        bond_id=bond.id,
        bond_code=bond.code,
        bond_name=bond.name,
        bond_type=bond.bond_type,
        event_type=event_type,
        event_date=event_date,
        event_title=EVENT_TITLES.get(event_type, event_type),
        coupon_rate=float(bond.coupon_rate) if bond.coupon_rate else None,
        issuer=bond.issuer,
    )


@router.get("/month", response_model=CalendarMonthOut)
async def get_month_events(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份", ge=1, le=12),
    bond_type: Optional[str] = Query(None, description="债券类型筛选"),
    event_type: Optional[str] = Query(None, description="事件类型筛选"),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    """
    获取指定月份的日历事件
    """
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    query = select(Bond)

    if bond_type:
        query = query.where(Bond.bond_type == bond_type)

    date_filters = []
    if not event_type or event_type == EVENT_TYPE_ISSUE:
        date_filters.append(
            and_(Bond.issue_date >= first_day, Bond.issue_date <= last_day)
        )
    if not event_type or event_type == EVENT_TYPE_MATURITY:
        date_filters.append(
            and_(Bond.maturity_date >= first_day, Bond.maturity_date <= last_day)
        )

    if date_filters:
        query = query.where(or_(*date_filters))

    result = await db.execute(query)
    bonds = result.scalars().all()

    days_map: dict[str, list[BondCalendarEvent]] = {}
    for day in range(1, last_day.day + 1):
        d = date(year, month, day)
        days_map[d.isoformat()] = []

    for bond in bonds:
        if (not event_type or event_type == EVENT_TYPE_ISSUE) and bond.issue_date:
            issue_date = bond.issue_date
            if first_day <= issue_date <= last_day:
                key = issue_date.isoformat()
                if key in days_map:
                    days_map[key].append(_create_event(bond, EVENT_TYPE_ISSUE, issue_date))

        if (not event_type or event_type == EVENT_TYPE_MATURITY) and bond.maturity_date:
            maturity_date = bond.maturity_date
            if first_day <= maturity_date <= last_day:
                key = maturity_date.isoformat()
                if key in days_map:
                    days_map[key].append(_create_event(bond, EVENT_TYPE_MATURITY, maturity_date))

    days = []
    for day in range(1, last_day.day + 1):
        d = date(year, month, day)
        events = days_map[d.isoformat()]
        days.append(CalendarDayEvents(
            date=d,
            events=events,
            event_count=len(events),
        ))

    return CalendarMonthOut(
        year=year,
        month=month,
        days=days,
    )


@router.get("/day", response_model=list[BondCalendarEvent])
async def get_day_events(
    target_date: date = Query(..., description="日期"),
    bond_type: Optional[str] = Query(None, description="债券类型筛选"),
    event_type: Optional[str] = Query(None, description="事件类型筛选"),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    """
    获取指定日期的事件列表
    """
    query = select(Bond)

    if bond_type:
        query = query.where(Bond.bond_type == bond_type)

    date_filters = []
    if not event_type or event_type == EVENT_TYPE_ISSUE:
        date_filters.append(Bond.issue_date == target_date)
    if not event_type or event_type == EVENT_TYPE_MATURITY:
        date_filters.append(Bond.maturity_date == target_date)

    if date_filters:
        query = query.where(or_(*date_filters))

    result = await db.execute(query)
    bonds = result.scalars().all()

    events = []
    for bond in bonds:
        if (not event_type or event_type == EVENT_TYPE_ISSUE) and bond.issue_date == target_date:
            events.append(_create_event(bond, EVENT_TYPE_ISSUE, target_date))
        if (not event_type or event_type == EVENT_TYPE_MATURITY) and bond.maturity_date == target_date:
            events.append(_create_event(bond, EVENT_TYPE_MATURITY, target_date))

    events.sort(key=lambda e: (e.event_type, e.bond_code))
    return events
