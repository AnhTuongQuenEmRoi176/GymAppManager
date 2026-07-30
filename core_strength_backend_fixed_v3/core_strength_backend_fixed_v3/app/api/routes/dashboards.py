from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import User
from app.db.session import get_db
from app.services.gym_queries import build_member_dashboard, build_trainer_dashboard


member_router = APIRouter(prefix="/member", tags=["Mobile - Hội viên"])
trainer_router = APIRouter(prefix="/trainer", tags=["Mobile - PT"])


@member_router.get("/dashboard")
def member_dashboard(
    current_user: User = Depends(require_roles("MEMBER")),
    db: Session = Depends(get_db),
):
    return build_member_dashboard(db, current_user.id)


@trainer_router.get("/dashboard")
def trainer_dashboard(
    current_user: User = Depends(require_roles("TRAINER")),
    db: Session = Depends(get_db),
):
    return build_trainer_dashboard(db, current_user.id)
