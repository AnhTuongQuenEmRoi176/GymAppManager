from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import (
    MemberPackage,
    MembershipRequest,
    Package,
    Payment,
    Trainer,
    User,
)
from app.db.session import get_db
from app.schemas.membership import MembershipRequestCreate
from app.services.gym_queries import get_member_profile
from app.utils.time import now_local


packages_router = APIRouter(prefix="/packages", tags=["Gói tập"])
member_router = APIRouter(prefix="/member", tags=["Mobile - Hội viên"])


@packages_router.get("")
def list_packages(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    stmt = select(Package).order_by(Package.price.asc())
    if active_only:
        stmt = stmt.where(Package.is_active.is_(True))
    packages = list(db.scalars(stmt))
    return [
        {
            "id": item.id,
            "name": item.name,
            "package_type": item.package_type,
            "description": item.description,
            "price": float(item.price),
            "duration_days": item.duration_days,
            "sessions": item.sessions,
            "is_active": bool(item.is_active),
        }
        for item in packages
    ]


@member_router.get("/memberships")
def membership_history(
    current_user: User = Depends(require_roles("MEMBER")),
    db: Session = Depends(get_db),
):
    member = get_member_profile(db, current_user.id)
    rows = db.execute(
        select(MemberPackage, Package)
        .join(Package, Package.id == MemberPackage.package_id)
        .where(MemberPackage.member_id == member.id)
        .order_by(MemberPackage.start_date.desc(), MemberPackage.id.desc())
    ).all()
    return [
        {
            "id": member_package.id,
            "package_id": package.id,
            "package_name": package.name,
            "package_type": package.package_type,
            "start_date": member_package.start_date.isoformat(),
            "end_date": member_package.end_date.isoformat(),
            "sessions_total": member_package.sessions_total,
            "sessions_remaining": member_package.sessions_remaining,
            "trainer_id": member_package.pt_id,
            "price_paid": float(member_package.price_paid),
            "status": member_package.status,
        }
        for member_package, package in rows
    ]


@member_router.get("/payments")
def payment_history(
    current_user: User = Depends(require_roles("MEMBER")),
    db: Session = Depends(get_db),
):
    member = get_member_profile(db, current_user.id)
    payments = list(
        db.scalars(
            select(Payment)
            .where(Payment.member_id == member.id)
            .order_by(Payment.created_at.desc())
        )
    )
    return [
        {
            "id": item.id,
            "payment_code": item.payment_code,
            "amount": float(item.amount),
            "method": item.method,
            "status": item.status,
            "paid_at": item.paid_at.isoformat() if item.paid_at else None,
            "note": item.note,
            "created_at": item.created_at.isoformat(),
        }
        for item in payments
    ]


@member_router.get("/requests")
def list_membership_requests(
    current_user: User = Depends(require_roles("MEMBER")),
    db: Session = Depends(get_db),
):
    member = get_member_profile(db, current_user.id)
    items = list(
        db.scalars(
            select(MembershipRequest)
            .where(MembershipRequest.member_id == member.id)
            .order_by(MembershipRequest.created_at.desc())
        )
    )
    return [
        {
            "id": item.id,
            "request_type": item.request_type,
            "requested_package_id": item.requested_package_id,
            "requested_trainer_id": item.requested_trainer_id,
            "note": item.note,
            "status": item.status,
            "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
            "created_at": item.created_at.isoformat(),
        }
        for item in items
    ]


@member_router.post("/requests")
def create_membership_request(
    payload: MembershipRequestCreate,
    current_user: User = Depends(require_roles("MEMBER")),
    db: Session = Depends(get_db),
):
    member = get_member_profile(db, current_user.id)
    if payload.requested_package_id is not None and db.get(Package, payload.requested_package_id) is None:
        raise HTTPException(status_code=404, detail="Gói tập được yêu cầu không tồn tại.")
    if payload.requested_trainer_id is not None and db.get(Trainer, payload.requested_trainer_id) is None:
        raise HTTPException(status_code=404, detail="PT được yêu cầu không tồn tại.")

    now = now_local()
    item = MembershipRequest(
        member_id=member.id,
        request_type=payload.request_type,
        requested_package_id=payload.requested_package_id,
        requested_trainer_id=payload.requested_trainer_id,
        note=payload.note,
        status="pending",
        reviewed_by=None,
        reviewed_at=None,
        created_at=now,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"message": "Đã gửi yêu cầu đến lễ tân.", "id": item.id}
