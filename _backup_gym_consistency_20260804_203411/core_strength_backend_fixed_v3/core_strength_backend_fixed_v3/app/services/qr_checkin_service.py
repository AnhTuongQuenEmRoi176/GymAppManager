from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased, joinedload

from app.core.security import (
    TokenError,
    create_qr_jwt,
    decode_qr_token,
    normalize_role,
    sha256_text,
)
from app.db.models import (
    Checkin,
    Member,
    MemberPackage,
    Notification,
    Package,
    PtSession,
    QrToken,
    Trainer,
    TrainingSchedule,
    User,
)
from app.services.gym_queries import active_member_package_row, get_member_profile, get_trainer_profile
from app.services.serializers import public_file_url
from app.utils.time import as_local_iso, now_local, today_local


def create_mobile_qr(db: Session, current_user: User, requested_type: str) -> dict:
    role = normalize_role(current_user.role.name if current_user.role else "")
    entity_type = "trainer" if requested_type.strip().upper() in {"TRAINER", "PT"} else "member"
    expected_role = "TRAINER" if entity_type == "trainer" else "MEMBER"
    if role != expected_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Loại QR không khớp với vai trò tài khoản.",
        )

    if entity_type == "member":
        entity_id = get_member_profile(db, current_user.id).id
    else:
        entity_id = get_trainer_profile(db, current_user.id).id

    now = now_local()
    # Vô hiệu QR cũ chưa sử dụng để mỗi tài khoản chỉ có một QR đang hoạt động.
    old_tokens = list(
        db.scalars(
            select(QrToken).where(
                QrToken.user_id == current_user.id,
                QrToken.used_at.is_(None),
                QrToken.expires_at > now,
            )
        )
    )
    for old in old_tokens:
        old.used_at = now

    token_id = str(uuid.uuid4())
    raw_token, expires_at = create_qr_jwt(
        user_id=current_user.id,
        entity_type=entity_type,
        entity_id=entity_id,
        token_id=token_id,
    )
    db.add(
        QrToken(
            token_id=token_id,
            user_id=current_user.id,
            entity_type=entity_type,
            entity_id=entity_id,
            token_hash=sha256_text(raw_token),
            expires_at=expires_at,
            used_at=None,
            used_by=None,
            created_at=now,
        )
    )
    db.commit()
    return {"token": raw_token, "expires_at": as_local_iso(expires_at)}


def _resolve_token(db: Session, raw_token: str, *, lock: bool = False) -> tuple[QrToken, dict]:
    try:
        payload = decode_qr_token(raw_token)
    except TokenError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    stmt = select(QrToken).where(
        QrToken.token_hash == sha256_text(raw_token),
        QrToken.token_id == str(payload.get("jti")),
    )
    if lock:
        stmt = stmt.with_for_update()
    record = db.scalar(stmt)
    now = now_local()
    if record is None:
        raise HTTPException(status_code=400, detail="Mã QR không tồn tại trong hệ thống.")
    if record.used_at is not None:
        raise HTTPException(status_code=409, detail="Mã QR đã được sử dụng.")
    if record.expires_at <= now:
        raise HTTPException(status_code=400, detail="Mã QR đã hết hạn.")
    if int(payload.get("sub", 0)) != record.user_id:
        raise HTTPException(status_code=400, detail="Mã QR không khớp tài khoản.")
    if int(payload.get("entity_id", 0)) != record.entity_id:
        raise HTTPException(status_code=400, detail="Mã QR không khớp hồ sơ.")
    return record, payload


def inspect_qr(db: Session, raw_token: str) -> dict:
    record, _payload = _resolve_token(db, raw_token)
    user = db.scalar(
        select(User).options(joinedload(User.role)).where(User.id == record.user_id)
    )
    if user is None or not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã ngừng hoạt động.")

    result = {
        "token_id": record.token_id,
        "entity_type": record.entity_type.upper(),
        "expires_at": as_local_iso(record.expires_at),
        "can_confirm": True,
        "reason": None,
        "person": {
            "user_id": user.id,
            "entity_id": record.entity_id,
            "full_name": user.full_name or user.username,
            "phone": user.phone,
            "email": user.email,
            "avatar": public_file_url(user.avatar),
            "role": normalize_role(user.role.name if user.role else record.entity_type),
        },
        "membership": None,
    }

    if record.entity_type == "member":
        row = active_member_package_row(db, record.entity_id)
        if row is None:
            result["can_confirm"] = False
            result["reason"] = "Hội viên không có gói tập còn hiệu lực."
        else:
            member_package, package, _trainer, trainer_user = row
            if (
                member_package.sessions_remaining is not None
                and member_package.sessions_remaining <= 0
            ):
                result["can_confirm"] = False
                result["reason"] = "Gói PT đã hết số buổi."
            result["membership"] = {
                "member_package_id": member_package.id,
                "package_name": package.name,
                "package_type": package.package_type,
                "start_date": member_package.start_date.isoformat(),
                "end_date": member_package.end_date.isoformat(),
                "sessions_remaining": member_package.sessions_remaining,
                "trainer_id": member_package.pt_id,
                "trainer_name": trainer_user.full_name if trainer_user else None,
                "status": member_package.status,
            }
    else:
        trainer = db.get(Trainer, record.entity_id)
        if trainer is None or (trainer.end_date is not None and trainer.end_date < today_local()):
            result["can_confirm"] = False
            result["reason"] = "PT đã ngừng làm việc."
        result["trainer"] = {
            "trainer_id": trainer.id if trainer else record.entity_id,
            "specialty": trainer.specialty if trainer else None,
        }
    return result


def _existing_checkin_by_idempotency(db: Session, key: str | None) -> Checkin | None:
    if not key:
        return None
    return db.scalar(select(Checkin).where(Checkin.idempotency_key == key))


def confirm_single_checkin(
    db: Session,
    *,
    raw_token: str,
    scanner_user: User,
    location: str | None,
    device_id: str | None,
    note: str | None,
    idempotency_key: str | None,
    manual_override: bool,
) -> dict:
    existing = _existing_checkin_by_idempotency(db, idempotency_key)
    if existing is not None:
        return {
            "message": "Yêu cầu đã được xử lý trước đó.",
            "checkin_id": existing.id,
            "status": existing.status,
            "scanned_at": as_local_iso(existing.scanned_at),
        }

    record, _payload = _resolve_token(db, raw_token, lock=True)
    info = inspect_qr(db, raw_token)
    if not info["can_confirm"] and not manual_override:
        raise HTTPException(status_code=409, detail=info["reason"])

    now = now_local()
    checkin = Checkin(
        member_id=record.entity_id if record.entity_type == "member" else None,
        trainer_id=record.entity_id if record.entity_type == "trainer" else None,
        scanned_at=now,
        scanner_user_id=scanner_user.id,
        source="QR Mobile",
        qr_payload=record.token_id,
        photo=None,
        status="confirmed",
        confirmed_at=now,
        pair_group_id=None,
        idempotency_key=idempotency_key,
        device_id=device_id,
        location=location or "Quầy check-in chính",
        note=note,
    )
    db.add(checkin)
    record.used_at = now
    record.used_by = scanner_user.id

    target_user_id = record.user_id
    db.add(
        Notification(
            user_id=target_user_id,
            type="checkin",
            title="Check-in thành công",
            body=f"Bạn đã check-in tại {location or 'Quầy check-in chính'}.",
            data_json={"entity_type": record.entity_type},
            is_read=False,
            read_at=None,
            created_at=now,
        )
    )
    db.commit()
    db.refresh(checkin)
    return {
        "message": "Xác nhận check-in thành công.",
        "checkin_id": checkin.id,
        "status": checkin.status,
        "entity_type": record.entity_type.upper(),
        "scanned_at": as_local_iso(checkin.scanned_at),
    }


def confirm_pair_checkin(
    db: Session,
    *,
    member_token: str,
    trainer_token: str,
    scanner_user: User,
    location: str | None,
    device_id: str | None,
    note: str | None,
    idempotency_key: str | None,
    manual_override: bool,
) -> dict:
    if idempotency_key:
        first = _existing_checkin_by_idempotency(db, f"{idempotency_key}:member")
        if first is not None:
            return {
                "message": "Yêu cầu quét đôi đã được xử lý trước đó.",
                "pair_group_id": first.pair_group_id,
                "member_checkin_id": first.id,
            }

    member_qr, _ = _resolve_token(db, member_token, lock=True)
    trainer_qr, _ = _resolve_token(db, trainer_token, lock=True)
    if member_qr.entity_type != "member" or trainer_qr.entity_type != "trainer":
        raise HTTPException(
            status_code=400,
            detail="Quét đôi yêu cầu đúng một QR hội viên và một QR PT.",
        )

    # Quét đôi phải dùng đúng gói PT/COMBO, không lấy nhầm gói GYM nếu hội viên
    # đang có nhiều gói hoạt động cùng lúc.
    today = today_local()
    pt_package_row = db.execute(
        select(MemberPackage, Package)
        .join(Package, Package.id == MemberPackage.package_id)
        .where(
            MemberPackage.member_id == member_qr.entity_id,
            MemberPackage.status == "active",
            MemberPackage.start_date <= today,
            MemberPackage.end_date >= today,
            Package.package_type.in_(["PT", "COMBO"]),
        )
        .order_by(
            (MemberPackage.pt_id == trainer_qr.entity_id).desc(),
            MemberPackage.end_date.desc(),
            MemberPackage.id.desc(),
        )
        .limit(1)
        .with_for_update()
    ).first()
    if pt_package_row is None:
        raise HTTPException(
            status_code=409,
            detail="Hội viên không có gói PT/COMBO còn hiệu lực.",
        )
    member_package, package = pt_package_row

    if member_package.sessions_remaining is None and not manual_override:
        raise HTTPException(
            status_code=409,
            detail="Gói hiện tại không có số buổi PT để xác nhận buổi tập đôi.",
        )
    if (member_package.sessions_remaining or 0) <= 0 and not manual_override:
        raise HTTPException(status_code=409, detail="Hội viên đã hết số buổi PT.")
    if (
        member_package.pt_id is not None
        and member_package.pt_id != trainer_qr.entity_id
        and not manual_override
    ):
        raise HTTPException(
            status_code=409,
            detail="PT được quét không phải PT đang phụ trách gói của hội viên.",
        )

    trainer = db.get(Trainer, trainer_qr.entity_id)
    if trainer is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ PT.")

    now = now_local()
    pair_group_id = str(uuid.uuid4())
    member_checkin = Checkin(
        member_id=member_qr.entity_id,
        trainer_id=None,
        scanned_at=now,
        scanner_user_id=scanner_user.id,
        source="QR Mobile Pair",
        qr_payload=member_qr.token_id,
        photo=None,
        status="confirmed",
        confirmed_at=now,
        pair_group_id=pair_group_id,
        idempotency_key=f"{idempotency_key}:member" if idempotency_key else None,
        device_id=device_id,
        location=location or "Quầy check-in chính",
        note=note,
    )
    trainer_checkin = Checkin(
        member_id=None,
        trainer_id=trainer_qr.entity_id,
        scanned_at=now,
        scanner_user_id=scanner_user.id,
        source="QR Mobile Pair",
        qr_payload=trainer_qr.token_id,
        photo=None,
        status="confirmed",
        confirmed_at=now,
        pair_group_id=pair_group_id,
        idempotency_key=f"{idempotency_key}:trainer" if idempotency_key else None,
        device_id=device_id,
        location=location or "Quầy check-in chính",
        note=note,
    )
    db.add_all([member_checkin, trainer_checkin])

    if member_package.sessions_remaining is not None and member_package.sessions_remaining > 0:
        member_package.sessions_remaining -= 1

    nearest_schedule = db.scalar(
        select(TrainingSchedule)
        .where(
            TrainingSchedule.member_id == member_qr.entity_id,
            TrainingSchedule.trainer_id == trainer_qr.entity_id,
            TrainingSchedule.status.in_(["pending", "upcoming"]),
            TrainingSchedule.start_at >= now - timedelta(hours=12),
            TrainingSchedule.start_at <= now + timedelta(hours=12),
        )
        .order_by(TrainingSchedule.start_at.asc())
        .limit(1)
        .with_for_update()
    )
    if nearest_schedule is not None:
        nearest_schedule.status = "completed"

    rate = Decimal(trainer.session_commission_percent or Decimal("0.50"))
    commission_amount = (
        Decimal(member_package.price_paid or 0) * rate / Decimal("100")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    pt_session = PtSession(
        trainer_id=trainer_qr.entity_id,
        member_id=member_qr.entity_id,
        member_package_id=member_package.id,
        schedule_id=nearest_schedule.id if nearest_schedule else None,
        session_date=now,
        confirmed_by=scanner_user.id,
        status="confirmed",
        commission_rate=rate,
        commission_amount=commission_amount,
        note=note,
        created_at=now,
    )
    db.add(pt_session)

    member_qr.used_at = now
    member_qr.used_by = scanner_user.id
    trainer_qr.used_at = now
    trainer_qr.used_by = scanner_user.id

    db.add_all(
        [
            Notification(
                user_id=member_qr.user_id,
                type="checkin",
                title="Buổi tập PT đã được xác nhận",
                body=(
                    "Hệ thống đã trừ 1 buổi PT. "
                    f"Số buổi còn lại: {member_package.sessions_remaining}."
                ),
                data_json={
                    "pair_group_id": pair_group_id,
                    "member_package_id": member_package.id,
                    "sessions_remaining": member_package.sessions_remaining,
                },
                is_read=False,
                read_at=None,
                created_at=now,
            ),
            Notification(
                user_id=trainer_qr.user_id,
                type="kpi",
                title="KPI buổi PT đã cập nhật",
                body="Một buổi PT mới đã được xác nhận vào KPI của bạn.",
                data_json={
                    "pair_group_id": pair_group_id,
                    "commission_amount": float(commission_amount),
                },
                is_read=False,
                read_at=None,
                created_at=now,
            ),
        ]
    )

    db.commit()
    db.refresh(member_checkin)
    db.refresh(trainer_checkin)
    db.refresh(pt_session)
    return {
        "message": "Xác nhận buổi tập PT thành công.",
        "pair_group_id": pair_group_id,
        "member_checkin_id": member_checkin.id,
        "trainer_checkin_id": trainer_checkin.id,
        "pt_session_id": pt_session.id,
        "member_package_id": member_package.id,
        "sessions_remaining": member_package.sessions_remaining,
        "commission_amount": float(commission_amount),
        "confirmed_at": as_local_iso(now),
    }
