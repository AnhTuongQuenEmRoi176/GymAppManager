from __future__ import annotations

import sys

from sqlalchemy import inspect, text

from app.core.config import settings
from app.db.session import engine


REQUIRED_TABLES = {
    "roles",
    "users",
    "members",
    "trainers",
    "packages",
    "member_packages",
    "training_schedules",
    "qr_tokens",
    "checkins",
    "pt_sessions",
    "notifications",
    "outbox_events",
}

REQUIRED_TRIGGERS = {
    "trg_checkins_after_insert",
    "trg_notifications_after_insert",
    "trg_schedules_after_insert",
    "trg_schedules_after_update",
    "trg_member_packages_after_insert",
    "trg_member_packages_after_update",
    "trg_pt_sessions_after_insert",
}


def main() -> int:
    print(f"DATABASE_URL: {settings.database_url}")
    try:
        with engine.connect() as conn:
            inspector = inspect(conn)
            tables = set(inspector.get_table_names())
            missing_tables = sorted(REQUIRED_TABLES - tables)

            trigger_rows = conn.execute(text("SHOW TRIGGERS FROM gym_db")).mappings().all()
            trigger_names = {str(row.get("Trigger")) for row in trigger_rows}
            missing_triggers = sorted(REQUIRED_TRIGGERS - trigger_names)

            sample_users = conn.execute(
                text(
                    "SELECT username, full_name FROM users "
                    "WHERE username IN ('member','trainer','admin','receptionist') "
                    "ORDER BY id"
                )
            ).mappings().all()

        if missing_tables:
            print("[ERROR] Thiếu bảng:", ", ".join(missing_tables))
        else:
            print("[OK] Đủ các bảng cần thiết.")

        if missing_triggers:
            print("[WARNING] Thiếu trigger realtime:", ", ".join(missing_triggers))
            print("          Hãy import database/realtime_triggers.sql")
        else:
            print("[OK] Đủ trigger realtime.")

        print("[INFO] Tài khoản mẫu tìm thấy:")
        for row in sample_users:
            print(f"  - {row['username']}: {row['full_name']}")

        return 1 if missing_tables else 0
    except Exception as exc:
        print("[ERROR] Không thể kết nối/kiểm tra database:", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
