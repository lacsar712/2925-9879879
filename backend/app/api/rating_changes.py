from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.bond import RatingChange, Bond
from app.schemas.bond import RatingChangeOut, RatingChangeListOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/rating-changes", tags=["评级变动"])


@router.get("", response_model=RatingChangeListOut)
async def list_rating_changes(
    change_type: Optional[str] = Query(None, description="变动类型：upgrade-上调, downgrade-下调, outlook-展望变动"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = select(RatingChange, Bond.code, Bond.name).join(Bond, RatingChange.bond_id == Bond.id)
    count_query = select(func.count(RatingChange.id))

    if change_type:
        types = change_type.split(",")
        query = query.where(RatingChange.change_type.in_(types))
        count_query = count_query.where(RatingChange.change_type.in_(types))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(RatingChange.effective_date.desc(), RatingChange.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for rc, code, name in rows:
        item = RatingChangeOut.model_validate(rc)
        item.bond_code = code
        item.bond_name = name
        items.append(item)

    return RatingChangeListOut(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{rating_change_id}", response_model=RatingChangeOut)
async def get_rating_change(
    rating_change_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await db.execute(
        select(RatingChange, Bond.code, Bond.name)
        .join(Bond, RatingChange.bond_id == Bond.id)
        .where(RatingChange.id == rating_change_id)
    )
    row = result.first()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="评级变动记录不存在")
    rc, code, name = row
    item = RatingChangeOut.model_validate(rc)
    item.bond_code = code
    item.bond_name = name
    return item
