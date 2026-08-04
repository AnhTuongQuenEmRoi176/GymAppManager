from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.api.deps import require_roles
from app.db.models import Member, MemberPackage, Package, Trainer, User
from app.db.session import get_db
from app.services.gym_queries import get_trainer_profile
from app.utils.time import today_local


router = APIRouter(prefix="/trainer", tags=["Mobile - PT"])


@router.get("/members")
def assigned_members(
    current_user: User = Depends(require_roles("TRAINER")),
    db: Session = Depends(get_db),
):
    trainer = get_trainer_profile(db, current_user.id)
    member_user = aliased(User)
    today = today_local()
    rows = db.execute(
        select(MemberPackage, Member, member_user, Package)
        .join(Member, Member.id == MemberPackage.member_id)
        .join(member_user, member_user.id == Member.user_id)
        .join(Package, Package.id == MemberPackage.package_id)
        .where(
            MemberPackage.pt_id == trainer.id,
            MemberPackage.status == "active",
            MemberPackage.start_date <= today,
            MemberPackage.end_date >= today,
        )
        .order_by(member_user.full_name.asc(), MemberPackage.end_date.desc())
    ).all()

    result: list[dict] = []
    seen: set[int] = set()
    for member_package, member, user, package in rows:
        if member.id in seen:
            continue
        seen.add(member.id)
        result.append(
            {
                "id": member.id,
                "member_package_id": member_package.id,
                "full_name": user.full_name or user.username,
                "phone": user.phone or "",
                "package_name": package.name,
                "end_date": member_package.end_date.isoformat(),
                "sessions_remaining": member_package.sessions_remaining or 0,
                "avatar": user.avatar,
            }
        )
    return result
