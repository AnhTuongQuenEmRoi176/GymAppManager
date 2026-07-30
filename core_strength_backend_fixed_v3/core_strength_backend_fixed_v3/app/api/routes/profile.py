from __future__ import annotations

import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import ProfileUpdateRequest
from app.services.serializers import user_to_dict
from app.utils.time import now_local


router = APIRouter(prefix="/profile", tags=["Hồ sơ"])


@router.get("")
def get_profile(current_user: User = Depends(get_current_user)):
    return user_to_dict(current_user)


@router.patch("")
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude_unset=True)
    if "phone" in data and data["phone"]:
        conflict = db.scalar(
            select(User.id).where(
                User.phone == data["phone"],
                User.id != current_user.id,
            )
        )
        if conflict:
            raise HTTPException(status_code=409, detail="Số điện thoại đã được sử dụng.")
    if "email" in data and data["email"]:
        data["email"] = str(data["email"])
        conflict = db.scalar(
            select(User.id).where(
                User.email == data["email"],
                User.id != current_user.id,
            )
        )
        if conflict:
            raise HTTPException(status_code=409, detail="Email đã được sử dụng.")

    for key, value in data.items():
        setattr(current_user, key, value)
    current_user.updated_at = now_local()
    db.commit()
    return user_to_dict(current_user)


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_types = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    extension = allowed_types.get(file.content_type or "")
    if extension is None:
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ ảnh JPG, PNG hoặc WEBP.")

    content = await file.read()
    max_bytes = settings.max_avatar_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Ảnh không được vượt quá {settings.max_avatar_size_mb} MB.",
        )

    avatar_dir = settings.upload_path / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)
    filename = f"user_{current_user.id}_{secrets.token_hex(8)}{extension}"
    target = avatar_dir / filename
    target.write_bytes(content)

    old_avatar = current_user.avatar
    current_user.avatar = f"uploads/avatars/{filename}"
    current_user.updated_at = now_local()
    db.commit()

    if old_avatar and old_avatar.startswith("uploads/avatars/"):
        old_path = settings.upload_path.parent / old_avatar
        if old_path.exists() and old_path != target:
            try:
                old_path.unlink()
            except OSError:
                pass

    return user_to_dict(current_user)
