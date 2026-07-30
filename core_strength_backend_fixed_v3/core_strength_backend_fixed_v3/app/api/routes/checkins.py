from __future__ import annotations

from datetime import date, datetime, time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.security import normalize_role
from app.db.models import Checkin, User
from app.db.session import get_db
from app.schemas.qr import (
    CheckinConfirmRequest,
    PairCheckinConfirmRequest,
    QrScanRequest,
)
from app.services.gym_queries import get_member_profile, get_trainer_profile
from app.services.qr_checkin_service import (
    confirm_pair_checkin,
    confirm_single_checkin,
    inspect_qr,
)


router = APIRouter(prefix="/checkins", tags=["Check-in"])


STATUS_LABELS = {
    "confirmed": "Thành công",
    "pending": "Chờ xác nhận",
    "rejected": "Từ chối",
}


@router.get("/history")
def checkin_history(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role = normalize_role(current_user.role.name if current_user.role else "")
    stmt = select(Checkin).order_by(Checkin.scanned_at.desc()).limit(limit)
    if role == "MEMBER":
        stmt = stmt.where(Checkin.member_id == get_member_profile(db, current_user.id).id)
    elif role == "TRAINER":
        stmt = stmt.where(Checkin.trainer_id == get_trainer_profile(db, current_user.id).id)
    elif role not in {"ADMIN", "RECEPTIONIST"}:
        return []

    if date_from:
        stmt = stmt.where(Checkin.scanned_at >= datetime.combine(date_from, time.min))
    if date_to:
        stmt = stmt.where(Checkin.scanned_at <= datetime.combine(date_to, time.max))

    records = list(db.scalars(stmt))
    return [
        {
            "id": item.id,
            "scanned_at": item.scanned_at.isoformat(),
            "location": item.location or "Phòng Gym",
            "status": STATUS_LABELS.get(item.status, item.status),
            "source": item.source or "QR Mobile",
            "pair_group_id": item.pair_group_id,
        }
        for item in records
    ]


@router.post("/scan")
def scan_qr(
    payload: QrScanRequest,
    _current_user: User = Depends(require_roles("ADMIN", "RECEPTIONIST")),
    db: Session = Depends(get_db),
):
    return inspect_qr(db, payload.token)


@router.post("/confirm")
def confirm_checkin(
    payload: CheckinConfirmRequest,
    current_user: User = Depends(require_roles("ADMIN", "RECEPTIONIST")),
    db: Session = Depends(get_db),
):
    return confirm_single_checkin(
        db,
        raw_token=payload.token,
        scanner_user=current_user,
        location=payload.location,
        device_id=payload.device_id,
        note=payload.note,
        idempotency_key=payload.idempotency_key,
        manual_override=payload.manual_override,
    )


@router.post("/confirm-pair")
def confirm_pair(
    payload: PairCheckinConfirmRequest,
    current_user: User = Depends(require_roles("ADMIN", "RECEPTIONIST")),
    db: Session = Depends(get_db),
):
    return confirm_pair_checkin(
        db,
        member_token=payload.member_token,
        trainer_token=payload.trainer_token,
        scanner_user=current_user,
        location=payload.location,
        device_id=payload.device_id,
        note=payload.note,
        idempotency_key=payload.idempotency_key,
        manual_override=payload.manual_override,
    )
