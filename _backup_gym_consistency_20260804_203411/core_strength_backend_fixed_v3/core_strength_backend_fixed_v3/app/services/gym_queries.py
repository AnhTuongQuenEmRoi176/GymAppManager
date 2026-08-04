from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.db.models import (
    Checkin,
    Member,
    MemberPackage,
    Notification,
    Package,
    PtSession,
    Trainer,
    TrainingSchedule,
    User,
)
from app.utils.time import month_bounds, now_local, today_local


def get_member_profile(db: Session, user_id: int) -> Member:
    member = db.scalar(select(Member).where(Member.user_id == user_id))
    if member is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ hội viên.")
    return member


def get_trainer_profile(db: Session, user_id: int) -> Trainer:
    trainer = db.scalar(select(Trainer).where(Trainer.user_id == user_id))
    if trainer is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ PT.")
    return trainer


def active_member_package_row(db: Session, member_id: int):
    trainer_user = aliased(User)
    today = today_local()
    stmt = (
        select(MemberPackage, Package, Trainer, trainer_user)
        .join(Package, Package.id == MemberPackage.package_id)
        .outerjoin(Trainer, Trainer.id == MemberPackage.pt_id)
        .outerjoin(trainer_user, trainer_user.id == Trainer.user_id)
        .where(
            MemberPackage.member_id == member_id,
            MemberPackage.status == "active",
            MemberPackage.start_date <= today,
            MemberPackage.end_date >= today,
        )
        .order_by(MemberPackage.end_date.desc(), MemberPackage.id.desc())
        .limit(1)
    )
    return db.execute(stmt).first()


def schedule_rows_for_member(
    db: Session,
    member_id: int,
    *,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    statuses: set[str] | None = None,
    limit: int | None = None,
):
    trainer_user = aliased(User)
    stmt = (
        select(TrainingSchedule, trainer_user)
        .join(Trainer, Trainer.id == TrainingSchedule.trainer_id)
        .join(trainer_user, trainer_user.id == Trainer.user_id)
        .where(TrainingSchedule.member_id == member_id)
        .order_by(TrainingSchedule.start_at.asc())
    )
    if date_from is not None:
        stmt = stmt.where(TrainingSchedule.start_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(TrainingSchedule.start_at <= date_to)
    if statuses:
        stmt = stmt.where(TrainingSchedule.status.in_(statuses))
    if limit:
        stmt = stmt.limit(limit)
    return db.execute(stmt).all()


def schedule_rows_for_trainer(
    db: Session,
    trainer_id: int,
    *,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    statuses: set[str] | None = None,
    limit: int | None = None,
):
    member_user = aliased(User)
    stmt = (
        select(TrainingSchedule, member_user)
        .join(Member, Member.id == TrainingSchedule.member_id)
        .join(member_user, member_user.id == Member.user_id)
        .where(TrainingSchedule.trainer_id == trainer_id)
        .order_by(TrainingSchedule.start_at.asc())
    )
    if date_from is not None:
        stmt = stmt.where(TrainingSchedule.start_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(TrainingSchedule.start_at <= date_to)
    if statuses:
        stmt = stmt.where(TrainingSchedule.status.in_(statuses))
    if limit:
        stmt = stmt.limit(limit)
    return db.execute(stmt).all()


def serialize_schedule(schedule: TrainingSchedule, participant_name: str) -> dict:
    return {
        "id": schedule.id,
        "title": schedule.title,
        "participant_name": participant_name,
        "start_at": schedule.start_at.isoformat(),
        "end_at": schedule.end_at.isoformat(),
        "status": schedule.status,
        "location": schedule.location,
        "note": schedule.note,
    }


def build_member_dashboard(db: Session, user_id: int) -> dict:
    member = get_member_profile(db, user_id)
    now = now_local()
    today = today_local()
    package_row = active_member_package_row(db, member.id)

    if package_row is None:
        membership = {
            "package_name": "Chưa có gói đang sử dụng",
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
            "sessions_remaining": None,
            "progress": 0.0,
            "trainer_name": None,
            "status": "Chưa có gói",
        }
    else:
        member_package, package, _trainer, trainer_user = package_row
        total_days = max((member_package.end_date - member_package.start_date).days, 1)
        used_days = max((today - member_package.start_date).days, 0)
        progress = min(max(used_days / total_days, 0.0), 1.0)
        remaining_days = (member_package.end_date - today).days
        status_text = "Sắp hết hạn" if remaining_days <= 7 else "Còn hạn"
        membership = {
            "package_name": package.name,
            "start_date": member_package.start_date.isoformat(),
            "end_date": member_package.end_date.isoformat(),
            "sessions_remaining": member_package.sessions_remaining,
            "progress": round(progress, 4),
            "trainer_name": trainer_user.full_name if trainer_user else None,
            "status": status_text,
        }

    month_start, month_end = month_bounds(today)
    monthly_checkins = db.scalar(
        select(func.count(Checkin.id)).where(
            Checkin.member_id == member.id,
            Checkin.status == "confirmed",
            Checkin.scanned_at >= month_start,
            Checkin.scanned_at <= month_end,
        )
    ) or 0

    upcoming_rows = schedule_rows_for_member(
        db,
        member.id,
        date_from=now,
        statuses={"pending", "upcoming"},
        limit=5,
    )
    upcoming_sessions = [
        serialize_schedule(schedule, trainer_user.full_name or "PT")
        for schedule, trainer_user in upcoming_rows
    ]

    activities: list[dict] = []
    checkins = list(
        db.scalars(
            select(Checkin)
            .where(Checkin.member_id == member.id)
            .order_by(Checkin.scanned_at.desc())
            .limit(5)
        )
    )
    for item in checkins:
        activities.append(
            {
                "id": item.id,
                "title": "Check-in thành công"
                if item.status == "confirmed"
                else "Check-in đang xử lý",
                "subtitle": f"{item.location or 'Phòng Gym'} • {item.source or 'QR Mobile'}",
                "occurred_at": item.scanned_at.isoformat(),
                "type": "checkin",
            }
        )

    notifications = list(
        db.scalars(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(5)
        )
    )
    for item in notifications:
        activities.append(
            {
                "id": 1_000_000 + item.id,
                "title": item.title,
                "subtitle": item.body,
                "occurred_at": item.created_at.isoformat(),
                "type": item.type,
            }
        )

    activities.sort(key=lambda item: item["occurred_at"], reverse=True)
    return {
        "membership": membership,
        "monthly_checkins": int(monthly_checkins),
        "upcoming_sessions": upcoming_sessions,
        "recent_activities": activities[:6],
    }


def build_trainer_dashboard(db: Session, user_id: int) -> dict:
    trainer = get_trainer_profile(db, user_id)
    today = today_local()
    now = now_local()
    day_start = datetime.combine(today, datetime.min.time())
    day_end = day_start + timedelta(days=1)
    month_start, month_end = month_bounds(today)

    today_session_count = db.scalar(
        select(func.count(TrainingSchedule.id)).where(
            TrainingSchedule.trainer_id == trainer.id,
            TrainingSchedule.start_at >= day_start,
            TrainingSchedule.start_at < day_end,
            TrainingSchedule.status.in_(["pending", "upcoming", "completed"]),
        )
    ) or 0

    assigned_members = db.scalar(
        select(func.count(func.distinct(MemberPackage.member_id))).where(
            MemberPackage.pt_id == trainer.id,
            MemberPackage.status == "active",
            MemberPackage.start_date <= today,
            MemberPackage.end_date >= today,
        )
    ) or 0

    monthly_sessions = db.scalar(
        select(func.count(PtSession.id)).where(
            PtSession.trainer_id == trainer.id,
            PtSession.status == "confirmed",
            PtSession.session_date >= month_start,
            PtSession.session_date <= month_end,
        )
    ) or 0

    session_income = db.scalar(
        select(func.coalesce(func.sum(PtSession.commission_amount), 0)).where(
            PtSession.trainer_id == trainer.id,
            PtSession.status == "confirmed",
            PtSession.session_date >= month_start,
            PtSession.session_date <= month_end,
        )
    ) or Decimal("0")
    estimated_income = Decimal(trainer.base_salary or 0) + Decimal(session_income)

    rows = schedule_rows_for_trainer(
        db,
        trainer.id,
        date_from=day_start,
        date_to=day_end,
        statuses={"pending", "upcoming", "completed"},
    )
    today_sessions = [
        serialize_schedule(schedule, member_user.full_name or "Hội viên")
        for schedule, member_user in rows
    ]

    member_user = aliased(User)
    package_rows = db.execute(
        select(MemberPackage, Member, member_user)
        .join(Member, Member.id == MemberPackage.member_id)
        .join(member_user, member_user.id == Member.user_id)
        .where(
            MemberPackage.pt_id == trainer.id,
            MemberPackage.status == "active",
            MemberPackage.start_date <= today,
            MemberPackage.end_date >= today,
            or_(
                and_(
                    MemberPackage.sessions_remaining.is_not(None),
                    MemberPackage.sessions_remaining <= 3,
                ),
                MemberPackage.end_date <= today + timedelta(days=7),
            ),
        )
        .order_by(MemberPackage.sessions_remaining.asc(), MemberPackage.end_date.asc())
        .limit(10)
    ).all()

    alerts: list[dict] = []
    for member_package, _member, user in package_rows:
        if member_package.sessions_remaining is not None and member_package.sessions_remaining <= 3:
            message = f"Sắp hết buổi tập, còn {member_package.sessions_remaining} buổi"
        else:
            days = (member_package.end_date - today).days
            message = f"Gói tập sẽ hết hạn sau {max(days, 0)} ngày"
        alerts.append(
            {
                "member_name": user.full_name or user.username,
                "message": message,
                "severity": "warning",
                "sessions_remaining": member_package.sessions_remaining,
            }
        )

    is_working = trainer.end_date is None or trainer.end_date >= today
    return {
        "is_working": is_working,
        "stats": {
            "today_sessions": int(today_session_count),
            "assigned_members": int(assigned_members),
            "monthly_sessions": int(monthly_sessions),
            "estimated_income": float(estimated_income),
        },
        "today_sessions": today_sessions,
        "alerts": alerts,
    }
