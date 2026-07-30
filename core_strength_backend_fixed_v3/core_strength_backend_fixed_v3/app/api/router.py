from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    auth,
    checkins,
    dashboards,
    devices,
    income,
    memberships,
    notifications,
    profile,
    qr,
    schedules,
    trainers,
)


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(auth.windows_router)
api_router.include_router(dashboards.member_router)
api_router.include_router(dashboards.trainer_router)
api_router.include_router(schedules.router)
api_router.include_router(qr.router)
api_router.include_router(checkins.router)
api_router.include_router(trainers.router)
api_router.include_router(notifications.router)
api_router.include_router(memberships.packages_router)
api_router.include_router(memberships.member_router)
api_router.include_router(profile.router)
api_router.include_router(devices.router)
api_router.include_router(income.router)
