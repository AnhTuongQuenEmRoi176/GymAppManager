from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def database_health(db: Session) -> bool:
    db.execute(text("SELECT 1"))
    return True
