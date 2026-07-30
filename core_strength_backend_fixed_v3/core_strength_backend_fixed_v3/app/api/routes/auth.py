from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutRequest,
    ProfileUpdateRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    MOBILE_ROLES,
    STAFF_ROLES,
    authenticate_user,
    create_password_reset_otp,
    issue_session,
    reset_password,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.services.serializers import user_to_dict


router = APIRouter(prefix="/auth", tags=["Xác thực Mobile"])
windows_router = APIRouter(prefix="/windows/auth", tags=["Xác thực Windows"])


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/login", response_model=TokenResponse)
def mobile_login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        account=payload.username,
        password=payload.password,
        allowed_roles=MOBILE_ROLES,
    )
    return issue_session(
        db,
        user=user,
        device_name=payload.device_name,
        ip_address=_client_ip(request),
    )


@windows_router.post("/login", response_model=TokenResponse)
def windows_login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        account=payload.username,
        password=payload.password,
        allowed_roles=STAFF_ROLES,
    )
    return issue_session(
        db,
        user=user,
        device_name=payload.device_name or "Windows App",
        ip_address=_client_ip(request),
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"user": user_to_dict(current_user)}


@router.post("/refresh", response_model=TokenResponse)
def refresh_session(
    payload: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return rotate_refresh_token(
        db,
        raw_refresh_token=payload.refresh_token,
        device_name=payload.device_name,
        ip_address=_client_ip(request),
    )


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    if payload.refresh_token:
        revoke_refresh_token(db, payload.refresh_token)
    return {"message": "Đăng xuất thành công."}


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    otp, user = create_password_reset_otp(db, payload.account)
    # Chưa cấu hình nhà cung cấp email/SMS. Ở môi trường dev trả OTP để kiểm thử.
    return {
        "message": (
            "Nếu tài khoản tồn tại, mã OTP đã được tạo. "
            "Trong môi trường thật hãy kết nối dịch vụ email hoặc SMS."
        ),
        "debug_otp": otp if settings.debug and user is not None else None,
    }


@router.post("/reset-password")
def perform_reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    reset_password(
        db,
        account=payload.account,
        otp=payload.otp,
        new_password=payload.new_password,
    )
    return {"message": "Đặt lại mật khẩu thành công."}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng.")
    current_user.password_hash = hash_password(payload.new_password)
    current_user.must_change_password = False
    db.commit()
    return {"message": "Đổi mật khẩu thành công."}
