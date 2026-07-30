from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import update, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Notification, User
from app.db.session import get_db
from app.utils.time import now_local


router = APIRouter(prefix="/notifications", tags=["Thông báo"])


@router.get("")
def list_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=300),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    items = list(db.scalars(stmt))
    return [
        {
            "id": item.id,
            "title": item.title,
            "body": item.body,
            "created_at": item.created_at.isoformat(),
            "type": item.type,
            "is_read": bool(item.is_read),
            "data": item.data_json,
        }
        for item in items
    ]


@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.get(Notification, notification_id)
    if item is None or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo.")
    if not item.is_read:
        item.is_read = True
        item.read_at = now_local()
        db.commit()
    return {"message": "Đã đánh dấu đã đọc."}


@router.post("/read-all")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.execute(
        update(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True, read_at=now_local())
    )
    db.commit()
    return {"message": "Đã đánh dấu toàn bộ thông báo là đã đọc."}
