from datetime import date, datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class RatingChangeOut(BaseModel):
    id: UUID
    bond_id: UUID
    agency: str
    change_type: str
    old_rating: Optional[str] = None
    new_rating: Optional[str] = None
    old_outlook: Optional[str] = None
    new_outlook: Optional[str] = None
    effective_date: date
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    bond_code: Optional[str] = None
    bond_name: Optional[str] = None

    model_config = {"from_attributes": True}


class RatingChangeListOut(BaseModel):
    items: list[RatingChangeOut]
    total: int
    page: int
    page_size: int


class BondOut(BaseModel):
    id: UUID
    code: str
    name: str
    full_name: Optional[str] = None
    bond_type: str
    issuer: str
    issue_date: Optional[date] = None
    maturity_date: Optional[date] = None
    coupon_rate: Optional[float] = None
    coupon_type: Optional[str] = None
    face_value: Optional[float] = 100.0
    credit_rating: Optional[str] = None
    remaining_term: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BondListOut(BaseModel):
    items: list[BondOut]
    total: int
    page: int
    page_size: int


class BondFilter(BaseModel):
    bond_type: Optional[str] = None
    credit_rating: Optional[str] = None
    keyword: Optional[str] = None
    page: int = 1
    page_size: int = 20
