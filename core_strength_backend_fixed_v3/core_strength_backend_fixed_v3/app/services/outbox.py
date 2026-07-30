from __future__ import annotations

import asyncio
import json
import logging
from contextlib import suppress
from typing import Any

from sqlalchemy import select

from app.core.config import settings
from app.db.models import OutboxEvent
from app.db.session import SessionLocal
from app.services.realtime import manager
from app.utils.time import now_local


logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self) -> None:
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if not settings.outbox_enabled or self._task is not None:
            return
        self._reset_processing_events()
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run(), name="outbox-worker")

    @staticmethod
    def _reset_processing_events() -> None:
        with SessionLocal() as db:
            events = list(db.scalars(select(OutboxEvent).where(OutboxEvent.status == "processing")))
            for event in events:
                event.status = "pending"
            if events:
                db.commit()

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is not None:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    async def _run(self) -> None:
        logger.info("Outbox worker đã khởi động.")
        while not self._stop_event.is_set():
            try:
                rows = await asyncio.to_thread(self._claim_batch)
                for row in rows:
                    await self._publish(row)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Lỗi vòng lặp outbox worker")
            await asyncio.sleep(max(settings.outbox_poll_seconds, 0.2))

    def _claim_batch(self) -> list[dict[str, Any]]:
        with SessionLocal() as db:
            events = list(
                db.scalars(
                    select(OutboxEvent)
                    .where(
                        OutboxEvent.status == "pending",
                        OutboxEvent.available_at <= now_local(),
                    )
                    .order_by(OutboxEvent.id.asc())
                    .limit(settings.outbox_batch_size)
                    .with_for_update()
                )
            )
            result: list[dict[str, Any]] = []
            for event in events:
                event.status = "processing"
                result.append(
                    {
                        "id": event.id,
                        "event_type": event.event_type,
                        "target_user_id": event.target_user_id,
                        "payload": event.payload_json,
                    }
                )
            db.commit()
            return result

    async def _publish(self, row: dict[str, Any]) -> None:
        event_id = int(row["id"])
        try:
            payload = row.get("payload") or {}
            if isinstance(payload, str):
                payload = json.loads(payload)
            if not isinstance(payload, dict):
                payload = {"value": payload}

            target_user_id = row.get("target_user_id")
            if target_user_id is None:
                await manager.broadcast(
                    event_type=str(row["event_type"]),
                    payload=payload,
                )
            else:
                await manager.send_to_user(
                    int(target_user_id),
                    event_type=str(row["event_type"]),
                    payload=payload,
                )
            await asyncio.to_thread(self._mark_published, event_id)
        except Exception as exc:
            logger.exception("Không thể publish outbox event id=%s", event_id)
            await asyncio.to_thread(self._mark_failed, event_id, str(exc))

    @staticmethod
    def _mark_published(event_id: int) -> None:
        with SessionLocal() as db:
            event = db.get(OutboxEvent, event_id)
            if event is None:
                return
            event.status = "published"
            event.published_at = now_local()
            event.last_error = None
            db.commit()

    @staticmethod
    def _mark_failed(event_id: int, error: str) -> None:
        with SessionLocal() as db:
            event = db.get(OutboxEvent, event_id)
            if event is None:
                return
            event.retry_count += 1
            event.last_error = error[:4000]
            event.status = "failed" if event.retry_count >= 5 else "pending"
            db.commit()


outbox_worker = OutboxWorker()
