from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.security import TokenError, decode_token
from app.db.health import database_health
from app.db.models import User
from app.db.session import SessionLocal
from app.services.outbox import outbox_worker
from app.services.realtime import manager


logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    try:
        with SessionLocal() as db:
            database_health(db)
        logger.info("Kết nối MySQL thành công.")
    except Exception:
        logger.exception(
            "Không thể kết nối MySQL. Kiểm tra XAMPP, database gym_db và DATABASE_URL."
        )
    outbox_worker.start()
    yield
    await outbox_worker.stop()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "REST API + WebSocket cho CORE STRENGTH Flutter và Windows App. "
        "Database dùng chung MySQL/XAMPP."
    ),
    debug=settings.debug,
    lifespan=lifespan,
)

allow_origins = settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials="*" not in allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_prefix)
app.mount("/uploads", StaticFiles(directory=settings.upload_path), name="uploads")


@app.get("/", tags=["Hệ thống"])
def root():
    return {
        "name": settings.app_name,
        "status": "running",
        "docs": "/docs",
        "api_prefix": settings.api_prefix,
    }


@app.get("/health", tags=["Hệ thống"])
def health():
    with SessionLocal() as db:
        database_health(db)
    return {"status": "ok", "database": "connected"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = decode_token(token, expected_type="access")
        user_id = int(payload["sub"])
    except (TokenError, ValueError, KeyError):
        await websocket.close(code=4401, reason="Token không hợp lệ hoặc đã hết hạn")
        return

    with SessionLocal() as db:
        user = db.scalar(
            select(User).options(joinedload(User.role)).where(User.id == user_id)
        )
        if user is None or not user.is_active:
            await websocket.close(code=4403, reason="Tài khoản không còn hoạt động")
            return

    await manager.connect(user_id, websocket)
    await websocket.send_json(
        {
            "type": "connection.ready",
            "payload": {"user_id": user_id},
        }
    )
    try:
        while True:
            message = await websocket.receive_text()
            if message.strip().lower() in {"ping", '{"type":"ping"}'}:
                await websocket.send_json({"type": "pong", "payload": {}})
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(user_id, websocket)
