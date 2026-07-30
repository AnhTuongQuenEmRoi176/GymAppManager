from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any

from fastapi import WebSocket

from app.utils.time import as_local_iso, now_local


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[user_id].add(websocket)

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._connections.get(user_id)
            if not sockets:
                return
            sockets.discard(websocket)
            if not sockets:
                self._connections.pop(user_id, None)

    async def send_to_user(
        self,
        user_id: int,
        *,
        event_type: str,
        payload: dict[str, Any],
    ) -> int:
        message = {
            "type": event_type,
            "received_at": as_local_iso(now_local()),
            "payload": payload,
        }
        async with self._lock:
            sockets = list(self._connections.get(user_id, set()))

        sent = 0
        stale: list[WebSocket] = []
        for socket in sockets:
            try:
                await socket.send_json(message)
                sent += 1
            except Exception:
                stale.append(socket)

        for socket in stale:
            await self.disconnect(user_id, socket)
        return sent

    async def broadcast(
        self,
        *,
        event_type: str,
        payload: dict[str, Any],
    ) -> int:
        async with self._lock:
            user_ids = list(self._connections.keys())
        total = 0
        for user_id in user_ids:
            total += await self.send_to_user(
                user_id,
                event_type=event_type,
                payload=payload,
            )
        return total

    async def online_user_count(self) -> int:
        async with self._lock:
            return len(self._connections)


manager = ConnectionManager()
