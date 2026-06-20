from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/user", tags=["user"])

ALLOWED_THEMES = {"dark", "light", "high-contrast"}


class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = Field(None, description="主题模式: dark, light, high-contrast")
    extra: Optional[Dict[str, Any]] = Field(None, description="其他设置项")


class UserSettingsResponse(BaseModel):
    theme: Optional[str] = None
    default_theme: Optional[str] = None
    extras: Dict[str, Any] = Field(default_factory=dict)


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
):
    settings = current_user.get_settings()
    return UserSettingsResponse(
        theme=settings.get("theme"),
        default_theme=settings.get("default_theme"),
        extras={k: v for k, v in settings.items() if k not in ("theme", "default_theme")},
    )


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    update_dict: Dict[str, Any] = {}

    if settings_update.theme is not None:
        if settings_update.theme not in ALLOWED_THEMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的主题值。允许的值: {', '.join(sorted(ALLOWED_THEMES))}",
            )
        update_dict["theme"] = settings_update.theme
        update_dict["default_theme"] = settings_update.theme

    if settings_update.extra is not None:
        for key, value in settings_update.extra.items():
            if key not in ("theme", "default_theme"):
                update_dict[key] = value

    if update_dict:
        current_user.set_settings(update_dict)
        await db.commit()

    settings = current_user.get_settings()
    return UserSettingsResponse(
        theme=settings.get("theme"),
        default_theme=settings.get("default_theme"),
        extras={k: v for k, v in settings.items() if k not in ("theme", "default_theme")},
    )
