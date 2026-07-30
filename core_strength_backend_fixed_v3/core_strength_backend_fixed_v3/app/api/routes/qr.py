from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import User
from app.db.session import get_db
from app.schemas.qr import QrTokenRequest, QrTokenResponse
from app.services.qr_checkin_service import create_mobile_qr


router = APIRouter(prefix="/qr", tags=["QR Mobile"])


@router.post("/token", response_model=QrTokenResponse)
def create_qr_token(
    payload: QrTokenRequest,
    current_user: User = Depends(require_roles("MEMBER", "TRAINER")),
    db: Session = Depends(get_db),
):
    return create_mobile_qr(db, current_user, payload.entity_type)
