from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import DeviceToken, User
from app.db.session import get_db
from app.schemas.membership import DeviceTokenRequest
from app.utils.time import now_local


router = APIRouter(prefix="/devices", tags=["Thiết bị Mobile"])


@router.post("/token")
def register_device_token(
    payload: DeviceTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = now_local()
    item = db.scalar(select(DeviceToken).where(DeviceToken.token == payload.token))
    if item is None:
        item = DeviceToken(
            user_id=current_user.id,
            token=payload.token,
            platform=payload.platform,
            device_name=payload.device_name,
            is_active=True,
            last_seen_at=now,
            created_at=now,
        )
        db.add(item)
    else:
        item.user_id = current_user.id
        item.platform = payload.platform
        item.device_name = payload.device_name
        item.is_active = True
        item.last_seen_at = now
    db.commit()
    return {"message": "Đã đăng ký thiết bị nhận thông báo."}


@router.delete("/token")
def unregister_device_token(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(
        select(DeviceToken).where(
            DeviceToken.token == token,
            DeviceToken.user_id == current_user.id,
        )
    )
    if item is not None:
        item.is_active = False
        item.last_seen_at = now_local()
        db.commit()
    return {"message": "Đã hủy thiết bị nhận thông báo."}
