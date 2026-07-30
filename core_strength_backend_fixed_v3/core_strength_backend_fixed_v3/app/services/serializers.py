from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.core.security import normalize_role
from app.db.models import User


def public_file_url(value: str | None) -> str | None:
    if not value:
        return None
    if value.startswith("http://") or value.startswith("https://"):
        return value
    normalized = value.replace("\\", "/").lstrip("/")
    if normalized.startswith("uploads/"):
        local_path = settings.upload_path.parent / normalized
        return (
            f"{settings.public_base_url.rstrip('/')}/{normalized}"
            if local_path.exists()
            else None
        )
    local_path = settings.upload_path / Path(normalized).name
    return (
        f"{settings.public_base_url.rstrip('/')}/uploads/{Path(normalized).name}"
        if local_path.exists()
        else None
    )


def user_to_dict(user: User) -> dict:
    role_name = normalize_role(user.role.name if user.role else "")
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name or user.username,
        "phone": user.phone,
        "email": user.email,
        "avatar": public_file_url(user.avatar),
        "role": role_name,
        "must_change_password": bool(user.must_change_password),
    }
