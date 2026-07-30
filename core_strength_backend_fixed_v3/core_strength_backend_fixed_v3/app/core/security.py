from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.utils.time import LOCAL_TZ


class TokenError(ValueError):
    pass


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode(
        "utf-8"
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(*, user_id: int, role: str) -> str:
    now = utc_now()
    payload = {
        "sub": str(user_id),
        "role": normalize_role(role),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(*, user_id: int, role: str) -> tuple[str, datetime]:
    now = utc_now()
    expires_at = now + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "role": normalize_role(role),
        "type": "refresh",
        "iat": now,
        "exp": expires_at,
        "jti": secrets.token_hex(24),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    expires_local = expires_at.astimezone(LOCAL_TZ).replace(tzinfo=None)
    return token, expires_local


def create_qr_jwt(
    *, user_id: int, entity_type: str, entity_id: int, token_id: str
) -> tuple[str, datetime]:
    now = utc_now()
    expires_at = now + timedelta(seconds=settings.qr_token_expire_seconds)
    payload = {
        "sub": str(user_id),
        "entity_type": entity_type.lower(),
        "entity_id": entity_id,
        "type": "qr",
        "jti": token_id,
        "iat": now,
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.qr_secret_key, algorithm=settings.jwt_algorithm)
    expires_local = expires_at.astimezone(LOCAL_TZ).replace(tzinfo=None)
    return token, expires_local


def decode_token(token: str, *, expected_type: str = "access") -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "type"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token đã hết hạn.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Token không hợp lệ.") from exc

    if payload.get("type") != expected_type:
        raise TokenError("Sai loại token.")
    return payload


def decode_qr_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.qr_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "type", "jti", "entity_id"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Mã QR đã hết hạn.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Mã QR không hợp lệ.") from exc

    if payload.get("type") != "qr":
        raise TokenError("Sai loại mã QR.")
    return payload


def normalize_role(role: str | None) -> str:
    value = (role or "").strip().upper()
    aliases = {
        "PT": "TRAINER",
        "HUẤN LUYỆN VIÊN": "TRAINER",
        "HỘI VIÊN": "MEMBER",
        "ADMINISTRATOR": "ADMIN",
        "RECEPTION": "RECEPTIONIST",
    }
    return aliases.get(value, value)


def credentials_exception(detail: str = "Không thể xác thực tài khoản.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
