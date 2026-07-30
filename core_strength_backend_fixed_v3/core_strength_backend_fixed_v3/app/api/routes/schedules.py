from __future__ import annotations

from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.security import normalize_role
from app.db.models import Member, MemberPackage, Trainer, TrainingSchedule, User
from app.db.session import get_db
from app.schemas.schedule import ScheduleCreateRequest, ScheduleUpdateRequest
from app.services.gym_queries import (
    get_member_profile,
    get_trainer_profile,
    schedule_rows_for_member,
    schedule_rows_for_trainer,
    serialize_schedule,
)
from app.utils.time import now_local, today_local


router = APIRouter(prefix="/schedules", tags=["Lịch tập và lịch dạy"])


def _to_datetime_start(value: date | None) -> datetime | None:
    return datetime.combine(value, time.min) if value else None


def _to_datetime_end(value: date | None) -> datetime | None:
    return datetime.combine(value, time.max) if value else None


def _has_conflict(
    db: Session,
    *,
    trainer_id: int,
    member_id: int,
    start_at: datetime,
    end_at: datetime,
    ignore_schedule_id: int | None = None,
) -> str | None:
    base_conditions = (
        TrainingSchedule.status.in_(["pending", "upcoming"]),
        TrainingSchedule.start_at < end_at,
        TrainingSchedule.end_at > start_at,
    )

    trainer_stmt = select(TrainingSchedule.id).where(
        TrainingSchedule.trainer_id == trainer_id,
        *base_conditions,
    )
    member_stmt = select(TrainingSchedule.id).where(
        TrainingSchedule.member_id == member_id,
        *base_conditions,
    )
    if ignore_schedule_id is not None:
        trainer_stmt = trainer_stmt.where(TrainingSchedule.id != ignore_schedule_id)
        member_stmt = member_stmt.where(TrainingSchedule.id != ignore_schedule_id)

    if db.scalar(trainer_stmt):
        return "PT đã có lịch trùng khung giờ này."
    if db.scalar(member_stmt):
        return "Hội viên đã có lịch trùng khung giờ này."
    return None


@router.get("")
def list_schedules(
    role: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actual_role = normalize_role(current_user.role.name if current_user.role else role)
    statuses = {status_filter} if status_filter else None
    if actual_role == "MEMBER":
        member = get_member_profile(db, current_user.id)
        rows = schedule_rows_for_member(
            db,
            member.id,
            date_from=_to_datetime_start(date_from),
            date_to=_to_datetime_end(date_to),
            statuses=statuses,
        )
    elif actual_role == "TRAINER":
        trainer = get_trainer_profile(db, current_user.id)
        rows = schedule_rows_for_trainer(
            db,
            trainer.id,
            date_from=_to_datetime_start(date_from),
            date_to=_to_datetime_end(date_to),
            statuses=statuses,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản staff cần dùng màn hình quản lý lịch trên Windows App.",
        )
    return [
        serialize_schedule(schedule, participant.full_name or participant.username)
        for schedule, participant in rows
    ]


@router.post("")
def create_schedule(
    payload: ScheduleCreateRequest,
    current_user: User = Depends(require_roles("ADMIN", "RECEPTIONIST", "TRAINER")),
    db: Session = Depends(get_db),
):
    current_role = normalize_role(current_user.role.name if current_user.role else "")

    if current_role == "TRAINER":
        trainer = get_trainer_profile(db, current_user.id)
        if payload.trainer_id is not None and payload.trainer_id != trainer.id:
            raise HTTPException(status_code=403, detail="PT chỉ được tạo lịch của chính mình.")
    else:
        if payload.trainer_id is None:
            raise HTTPException(status_code=400, detail="Thiếu trainer_id khi tạo lịch cho PT.")
        trainer = db.get(Trainer, payload.trainer_id)
        if trainer is None:
            raise HTTPException(status_code=404, detail="PT không tồn tại.")

    member = db.get(Member, payload.member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Hội viên không tồn tại.")

    package: MemberPackage | None = None
    if payload.member_package_id is not None:
        package = db.get(MemberPackage, payload.member_package_id)
        if package is None or package.member_id != payload.member_id:
            raise HTTPException(status_code=400, detail="Gói tập không thuộc hội viên.")
        if package.pt_id != trainer.id:
            raise HTTPException(status_code=400, detail="Hội viên chưa được gán cho PT này.")
        today = today_local()
        if package.status != "active" or package.start_date > today or package.end_date < today:
            raise HTTPException(status_code=400, detail="Gói PT của hội viên không còn hiệu lực.")
        if package.sessions_remaining is not None and package.sessions_remaining <= 0:
            raise HTTPException(status_code=400, detail="Gói PT của hội viên đã hết số buổi.")
    elif current_role == "TRAINER":
        raise HTTPException(
            status_code=400,
            detail="Cần chọn gói PT đang hoạt động của hội viên.",
        )

    start_at = payload.start_at.replace(tzinfo=None)
    end_at = payload.end_at.replace(tzinfo=None)
    if start_at < now_local().replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="Không thể tạo lịch ở thời điểm đã qua.")

    conflict_message = _has_conflict(
        db,
        trainer_id=trainer.id,
        member_id=member.id,
        start_at=start_at,
        end_at=end_at,
    )
    if conflict_message:
        raise HTTPException(status_code=409, detail=conflict_message)

    now = now_local()
    schedule = TrainingSchedule(
        trainer_id=trainer.id,
        member_id=member.id,
        member_package_id=package.id if package else None,
        title=payload.title.strip(),
        start_at=start_at,
        end_at=end_at,
        location=payload.location.strip() if payload.location else None,
        note=payload.note.strip() if payload.note else None,
        status="upcoming",
        created_by=current_user.id,
        cancelled_by=None,
        cancelled_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return {"message": "Tạo lịch thành công.", "id": schedule.id}


@router.patch("/{schedule_id}")
def update_schedule(
    schedule_id: int,
    payload: ScheduleUpdateRequest,
    current_user: User = Depends(require_roles("ADMIN", "RECEPTIONIST", "TRAINER")),
    db: Session = Depends(get_db),
):
    schedule = db.get(TrainingSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch tập.")

    role = normalize_role(current_user.role.name if current_user.role else "")
    if role == "TRAINER":
        trainer = get_trainer_profile(db, current_user.id)
        if schedule.trainer_id != trainer.id:
            raise HTTPException(status_code=403, detail="Bạn không được sửa lịch của PT khác.")
        if schedule.status in {"completed", "cancelled", "no_show"}:
            raise HTTPException(status_code=400, detail="Lịch này đã kết thúc nên không thể sửa.")

    data = payload.model_dump(exclude_unset=True)
    if "start_at" in data and data["start_at"] is not None:
        data["start_at"] = data["start_at"].replace(tzinfo=None)
    if "end_at" in data and data["end_at"] is not None:
        data["end_at"] = data["end_at"].replace(tzinfo=None)

    start_at = data.get("start_at", schedule.start_at)
    end_at = data.get("end_at", schedule.end_at)
    if end_at <= start_at:
        raise HTTPException(status_code=400, detail="Thời gian kết thúc phải sau bắt đầu.")
    if data.get("status") != "cancelled" and start_at < now_local().replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="Không thể chuyển lịch sang thời điểm đã qua.")

    if data.get("status") != "cancelled":
        conflict_message = _has_conflict(
            db,
            trainer_id=schedule.trainer_id,
            member_id=schedule.member_id,
            start_at=start_at,
            end_at=end_at,
            ignore_schedule_id=schedule.id,
        )
        if conflict_message:
            raise HTTPException(status_code=409, detail=conflict_message)

    for key, value in data.items():
        if key in {"title", "location", "note"} and isinstance(value, str):
            value = value.strip() or None
        setattr(schedule, key, value)

    if data.get("status") == "cancelled":
        schedule.cancelled_by = current_user.id
        schedule.cancelled_at = now_local()
    schedule.updated_at = now_local()
    db.commit()
    return {"message": "Cập nhật lịch thành công."}
