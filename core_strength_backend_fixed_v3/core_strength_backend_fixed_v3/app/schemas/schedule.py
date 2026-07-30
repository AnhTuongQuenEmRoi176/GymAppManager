from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ScheduleCreateRequest(BaseModel):
    # Với tài khoản PT trên mobile có thể bỏ trainer_id; backend tự lấy PT hiện tại.
    # Admin/lễ tân vẫn phải truyền trainer_id khi tạo lịch từ API quản trị.
    trainer_id: int | None = None
    member_id: int
    member_package_id: int | None = None
    title: str = Field(min_length=2, max_length=200)
    start_at: datetime
    end_at: datetime
    location: str | None = Field(default=None, max_length=200)
    note: str | None = None

    @model_validator(mode="after")
    def validate_time(self) -> "ScheduleCreateRequest":
        if self.end_at <= self.start_at:
            raise ValueError("Thời gian kết thúc phải sau thời gian bắt đầu.")
        return self


class ScheduleUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = Field(default=None, max_length=200)
    note: str | None = None
    status: str | None = Field(
        default=None,
        pattern="^(pending|upcoming|completed|cancelled|no_show)$",
    )
