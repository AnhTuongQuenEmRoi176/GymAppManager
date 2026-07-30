from __future__ import annotations

import secrets
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    normalize_role,
    sha256_text,
    verify_password,
)
from app.db.models import PasswordResetOtp, RefreshToken, User
from app.services.serializers import user_to_dict
from app.utils.time import now_local


MOBILE_ROLES = {"MEMBER", "TRAINER"}
STAFF_ROLES = {"ADMIN", "RECEPTIONIST"}


def find_user_by_account(db: Session, account: str) -> User | None:
    normalized = account.strip()
    return db.scalar(
        select(User)
        .options(joinedload(User.role))
        .where(
            or_(
                User.username == normalized,
                User.phone == normalized,
                User.email == normalized,
            )
        )
    )


def authenticate_user(
    db: Session,
    *,
    account: str,
    password: str,
    allowed_roles: set[str] | None = None,
) -> User:
    user = find_user_by_account(db, account)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa hoặc ngừng hoạt động.",
        )
    role = normalize_role(user.role.name if user.role else "")
    if allowed_roles is not None and role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không được phép đăng nhập trên ứng dụng này.",
        )
    return user


def issue_session(
    db: Session,
    *,
    user: User,
    device_name: str | None,
    ip_address: str | None,
) -> dict:
    role = normalize_role(user.role.name if user.role else "")
    access_token = create_access_token(user_id=user.id, role=role)
    refresh_token, refresh_expires = create_refresh_token(user_id=user.id, role=role)
    now = now_local()

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=sha256_text(refresh_token),
            expires_at=refresh_expires,
            revoked_at=None,
            device_name=device_name,
            ip_address=ip_address,
            created_at=now,
        )
    )
    user.last_login_at = now
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": user_to_dict(user),
    }


def rotate_refresh_token(
    db: Session,
    *,
    raw_refresh_token: str,
    device_name: str | None,
    ip_address: str | None,
) -> dict:
    try:
        payload = decode_token(raw_refresh_token, expected_type="refresh")
        user_id = int(payload["sub"])
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ.",
        ) from exc

    token_record = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == sha256_text(raw_refresh_token),
            RefreshToken.user_id == user_id,
        )
    )
    now = now_local()
    if (
        token_record is None
        or token_record.revoked_at is not None
        or token_record.expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token đã hết hạn hoặc bị thu hồi.",
        )

    user = db.scalar(
        select(User).options(joinedload(User.role)).where(User.id == user_id)
    )
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Tài khoản không còn hợp lệ.")

    token_record.revoked_at = now
    db.flush()
    return issue_session(
        db,
        user=user,
        device_name=device_name or token_record.device_name,
        ip_address=ip_address,
    )


def revoke_refresh_token(db: Session, raw_refresh_token: str) -> None:
    record = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == sha256_text(raw_refresh_token)
        )
    )
    if record is not None and record.revoked_at is None:
        record.revoked_at = now_local()
        db.commit()


def create_password_reset_otp(db: Session, account: str) -> tuple[str, User | None]:
    user = find_user_by_account(db, account)
    if user is None or not user.is_active:
        # Không tiết lộ tài khoản có tồn tại hay không.
        return "000000", None

    now = now_local()
    db.execute(
        update(PasswordResetOtp)
        .where(
            PasswordResetOtp.user_id == user.id,
            PasswordResetOtp.used_at.is_(None),
        )
        .values(used_at=now)
    )

    otp = f"{secrets.randbelow(1_000_000):06d}"
    db.add(
        PasswordResetOtp(
            user_id=user.id,
            otp_hash=sha256_text(otp),
            expires_at=now + timedelta(minutes=settings.password_reset_otp_minutes),
            used_at=None,
            attempt_count=0,
            created_at=now,
        )
    )
    db.commit()
    return otp, user


def reset_password(
    db: Session,
    *,
    account: str,
    otp: str,
    new_password: str,
) -> None:
    user = find_user_by_account(db, account)
    if user is None:
        raise HTTPException(status_code=400, detail="OTP hoặc tài khoản không hợp lệ.")

    now = now_local()
    record = db.scalar(
        select(PasswordResetOtp)
        .where(
            PasswordResetOtp.user_id == user.id,
            PasswordResetOtp.used_at.is_(None),
        )
        .order_by(PasswordResetOtp.id.desc())
    )
    if record is None or record.expires_at <= now or record.attempt_count >= 5:
        raise HTTPException(status_code=400, detail="OTP đã hết hạn hoặc không hợp lệ.")

    record.attempt_count += 1
    if not secrets.compare_digest(record.otp_hash, sha256_text(otp)):
        db.commit()
        raise HTTPException(status_code=400, detail="OTP đã hết hạn hoặc không hợp lệ.")

    record.used_at = now
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )
    db.commit()
