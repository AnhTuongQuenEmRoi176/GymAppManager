from __future__ import annotations

from pydantic import BaseModel, Field


class QrTokenRequest(BaseModel):
    entity_type: str = Field(pattern="^(MEMBER|TRAINER|PT|member|trainer|pt)$")


class QrTokenResponse(BaseModel):
    token: str
    expires_at: str


class QrScanRequest(BaseModel):
    token: str = Field(min_length=20)


class CheckinConfirmRequest(BaseModel):
    token: str = Field(min_length=20)
    location: str | None = Field(default="Quầy check-in chính", max_length=200)
    device_id: str | None = Field(default=None, max_length=150)
    note: str | None = Field(default=None, max_length=500)
    idempotency_key: str | None = Field(default=None, max_length=100)
    manual_override: bool = False


class PairCheckinConfirmRequest(BaseModel):
    member_token: str = Field(min_length=20)
    trainer_token: str = Field(min_length=20)
    location: str | None = Field(default="Quầy check-in chính", max_length=200)
    device_id: str | None = Field(default=None, max_length=150)
    note: str | None = Field(default=None, max_length=500)
    idempotency_key: str | None = Field(default=None, max_length=100)
    manual_override: bool = False
