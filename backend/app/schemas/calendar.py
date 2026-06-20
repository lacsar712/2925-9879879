from datetime import date
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class BondCalendarEvent(BaseModel):
    id: UUID
    bond_id: UUID
    bond_code: str
    bond_name: str
    bond_type: str
    event_type: str
    event_date: date
    event_title: str
    coupon_rate: Optional[float] = None
    issuer: Optional[str] = None

    model_config = {"from_attributes": True}


class CalendarDayEvents(BaseModel):
    date: date
    events: list[BondCalendarEvent]
    event_count: int


class CalendarMonthOut(BaseModel):
    year: int
    month: int
    days: list[CalendarDayEvents]
