from __future__ import annotations

from pydantic import BaseModel, Field


class MembershipRequestCreate(BaseModel):
    request_type: str = Field(
        pattern="^(new_package|renew|upgrade|cancel|change_trainer)$"
    )
    requested_package_id: int | None = None
    requested_trainer_id: int | None = None
    note: str | None = None


class DeviceTokenRequest(BaseModel):
    token: str = Field(min_length=10, max_length=500)
    platform: str = Field(pattern="^(android|ios|web)$")
    device_name: str | None = Field(default=None, max_length=150)
