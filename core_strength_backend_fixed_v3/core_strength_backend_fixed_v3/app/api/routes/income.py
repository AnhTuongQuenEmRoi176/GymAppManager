from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import PtSession, Trainer, User
from app.db.session import get_db
from app.services.gym_queries import get_trainer_profile
from app.utils.time import month_bounds, today_local


router = APIRouter(prefix="/trainer", tags=["Mobile - Thu nhập PT"])


@router.get("/income")
def trainer_income(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=2100),
    current_user: User = Depends(require_roles("TRAINER")),
    db: Session = Depends(get_db),
):
    trainer = get_trainer_profile(db, current_user.id)
    today = today_local()
    target = date(year or today.year, month or today.month, 1)
    start_at, end_at = month_bounds(target)
    sessions = list(
        db.scalars(
            select(PtSession)
            .where(
                PtSession.trainer_id == trainer.id,
                PtSession.status == "confirmed",
                PtSession.session_date >= start_at,
                PtSession.session_date <= end_at,
            )
            .order_by(PtSession.session_date.desc())
        )
    )
    session_income = sum((Decimal(item.commission_amount or 0) for item in sessions), Decimal("0"))
    total = Decimal(trainer.base_salary or 0) + session_income
    return {
        "month": target.month,
        "year": target.year,
        "base_salary": float(trainer.base_salary or 0),
        "session_count": len(sessions),
        "session_income": float(session_income),
        "total_income": float(total),
        "sessions": [
            {
                "id": item.id,
                "member_id": item.member_id,
                "session_date": item.session_date.isoformat(),
                "commission_rate": float(item.commission_rate),
                "commission_amount": float(item.commission_amount),
                "note": item.note,
            }
            for item in sessions
        ],
    }
