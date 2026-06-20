from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.bond import MarketSource
from app.models.user import User
from app.schemas.user import UserOut
from app.api.deps import require_admin

router = APIRouter(prefix="/api/admin", tags=["系统管理"])


@router.get("/sources")
async def get_sources(db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(MarketSource).order_by(MarketSource.name))
    sources = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "source_type": s.source_type,
            "status": s.status,
            "description": s.description,
            "is_enabled": s.is_enabled,
        }
        for s in sources
    ]


@router.put("/sources/{source_id}")
async def update_source(
    source_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    result = await db.execute(select(MarketSource).where(MarketSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="行情源不存在")

    if "status" in body:
        source.status = body["status"]
    if "is_enabled" in body:
        source.is_enabled = body["is_enabled"]
    if "description" in body:
        source.description = body["description"]

    await db.flush()
    return {"message": "更新成功"}


@router.get("/users", response_model=list[UserOut])
async def get_users(db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(User).order_by(User.created_at))
    return [UserOut.model_validate(u) for u in result.scalars().all()]


@router.get("/data-quality/overview")
async def get_data_quality_overview(db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(MarketSource))
    sources = result.scalars().all()

    enabled_sources = [s for s in sources if s.is_enabled]
    disabled_count = len(sources) - len(enabled_sources)

    online_count = sum(1 for s in enabled_sources if s.status == "online")
    error_count = sum(1 for s in enabled_sources if s.status == "error")
    offline_count = sum(1 for s in enabled_sources if s.status == "offline")

    healthy_count = sum(1 for s in enabled_sources if s.health_score is not None and s.health_score >= 80)
    warning_count = sum(1 for s in enabled_sources if s.health_score is not None and 60 <= s.health_score < 80)
    critical_count = sum(1 for s in enabled_sources if s.health_score is not None and s.health_score < 60)

    avg_latency_list = [s.avg_latency_ms for s in enabled_sources if s.avg_latency_ms is not None]
    avg_latency = sum(avg_latency_list) / len(avg_latency_list) if avg_latency_list else 0

    total_missing = sum(s.today_missing_quotes or 0 for s in enabled_sources)
    total_inverted = sum(s.today_inverted_spreads or 0 for s in enabled_sources)

    health_scores = [s.health_score for s in enabled_sources if s.health_score is not None]
    avg_health = sum(health_scores) / len(health_scores) if health_scores else 0

    return {
        "total_sources": len(sources),
        "enabled_sources": len(enabled_sources),
        "disabled_sources": disabled_count,
        "online_sources": online_count,
        "offline_sources": offline_count,
        "error_sources": error_count,
        "healthy_sources": healthy_count,
        "warning_sources": warning_count,
        "critical_sources": critical_count,
        "avg_latency_ms": round(avg_latency, 2),
        "total_missing_quotes": total_missing,
        "total_inverted_spreads": total_inverted,
        "avg_health_score": round(avg_health, 2),
    }


@router.get("/data-quality/sources")
async def get_data_quality_sources(db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(MarketSource).order_by(MarketSource.name))
    sources = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "name": s.name,
            "source_type": s.source_type,
            "status": s.status,
            "is_enabled": s.is_enabled,
            "last_heartbeat": s.last_heartbeat.isoformat() if s.last_heartbeat else None,
            "avg_latency_ms": float(s.avg_latency_ms) if s.avg_latency_ms is not None else None,
            "today_missing_quotes": s.today_missing_quotes or 0,
            "today_inverted_spreads": s.today_inverted_spreads or 0,
            "health_score": float(s.health_score) if s.health_score is not None else None,
            "description": s.description,
        }
        for s in sources
    ]
