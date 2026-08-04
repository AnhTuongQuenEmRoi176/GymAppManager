import json
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import text

from app.db import get_session
from app.state import get_current_user, is_admin
from app.ui.theme import configure_table, page_title


ROLE_MEMBER_NAMES = ("member",)
ROLE_TRAINER_NAMES = ("trainer",)


class NotificationRepository:
    """Truy vấn thông báo bằng SQL thuần để không bắt buộc sửa app/models.py."""

    @staticmethod
    def list_mobile_users(session):
        rows = session.execute(
            text(
                """
                SELECT
                    u.id,
                    COALESCE(NULLIF(u.full_name, ''), u.username) AS full_name,
                    u.username,
                    r.name AS role_display,
                    LOWER(r.name) AS role_name
                FROM users u
                JOIN roles r ON r.id = u.role_id
                WHERE u.is_active = 1
                  AND LOWER(r.name) IN ('member', 'trainer')
                ORDER BY LOWER(r.name), full_name
                """
            )
        ).mappings().all()
        return list(rows)

    @staticmethod
    def target_users(session, audience, specific_user_id=None):
        base_sql = """
            SELECT u.id, COALESCE(NULLIF(u.full_name, ''), u.username) AS full_name,
                   LOWER(r.name) AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.is_active = 1
        """
        params = {}

        if audience == "members":
            base_sql += " AND LOWER(r.name) = 'member'"
        elif audience == "trainers":
            base_sql += " AND LOWER(r.name) = 'trainer'"
        elif audience == "all_mobile":
            base_sql += " AND LOWER(r.name) IN ('member', 'trainer')"
        elif audience == "specific":
            base_sql += " AND u.id = :user_id AND LOWER(r.name) IN ('member', 'trainer')"
            params["user_id"] = specific_user_id
        else:
            return []

        base_sql += " ORDER BY full_name"
        return list(session.execute(text(base_sql), params).mappings().all())

    @staticmethod
    def has_notification_trigger(session):
        row = session.execute(
            text(
                """
                SELECT COUNT(*) AS total
                FROM information_schema.TRIGGERS
                WHERE TRIGGER_SCHEMA = DATABASE()
                  AND TRIGGER_NAME = 'trg_notifications_after_insert'
                """
            )
        ).mappings().first()
        return bool(row and int(row["total"] or 0) > 0)

    @staticmethod
    def send(session, *, audience, specific_user_id, notification_type, title, body, priority, route):
        targets = NotificationRepository.target_users(
            session,
            audience=audience,
            specific_user_id=specific_user_id,
        )
        if not targets:
            raise ValueError("Không tìm thấy tài khoản mobile phù hợp để gửi thông báo.")

        current_user = get_current_user()
        sender_id = current_user.id if current_user else None
        has_trigger = NotificationRepository.has_notification_trigger(session)
        created_at = datetime.now()

        for target in targets:
            payload = {
                "priority": priority,
                "route": route or None,
                "sender_user_id": sender_id,
                "recipient_role": target["role_name"],
            }
            result = session.execute(
                text(
                    """
                    INSERT INTO notifications
                        (user_id, type, title, body, data_json, is_read, read_at, created_at)
                    VALUES
                        (:user_id, :type, :title, :body, :data_json, 0, NULL, :created_at)
                    """
                ),
                {
                    "user_id": target["id"],
                    "type": notification_type,
                    "title": title,
                    "body": body,
                    "data_json": json.dumps(payload, ensure_ascii=False),
                    "created_at": created_at,
                },
            )
            notification_id = int(result.lastrowid)

            # Nếu database chưa cài trigger realtime thì tự tạo outbox event.
            if not has_trigger:
                session.execute(
                    text(
                        """
                        INSERT INTO outbox_events
                            (event_type, aggregate_type, aggregate_id, target_user_id,
                             payload_json, status, retry_count, available_at, created_at)
                        VALUES
                            ('notification.created', 'notification', :aggregate_id, :target_user_id,
                             :payload_json, 'pending', 0, :created_at, :created_at)
                        """
                    ),
                    {
                        "aggregate_id": str(notification_id),
                        "target_user_id": target["id"],
                        "payload_json": json.dumps(
                            {
                                "notification_id": notification_id,
                                "type": notification_type,
                                "title": title,
                                "created_at": created_at.isoformat(timespec="seconds"),
                            },
                            ensure_ascii=False,
                        ),
                        "created_at": created_at,
                    },
                )

        session.commit()
        return targets

    @staticmethod
    def list_recent(session, search_text="", notification_type="all", limit=300):
        sql = """
            SELECT
                n.id,
                COALESCE(NULLIF(u.full_name, ''), u.username) AS recipient_name,
                r.name AS role_display,
                n.type,
                n.title,
                n.is_read,
                n.created_at
            FROM notifications n
            JOIN users u ON u.id = n.user_id
            LEFT JOIN roles r ON r.id = u.role_id
            WHERE 1 = 1
        """
        params = {"limit_value": int(limit)}
        if search_text:
            sql += " AND (u.full_name LIKE :term OR u.username LIKE :term OR n.title LIKE :term)"
            params["term"] = f"%{search_text}%"
        if notification_type != "all":
            sql += " AND n.type = :notification_type"
            params["notification_type"] = notification_type
        sql += " ORDER BY n.created_at DESC, n.id DESC LIMIT :limit_value"
        return list(session.execute(text(sql), params).mappings().all())

    @staticmethod
    def statistics(session):
        return session.execute(
            text(
                """
                SELECT
                    SUM(CASE WHEN DATE(created_at) = CURDATE() THEN 1 ELSE 0 END) AS sent_today,
                    SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) AS unread_total,
                    COUNT(DISTINCT user_id) AS recipient_total,
                    COUNT(*) AS notification_total
                FROM notifications
                """
            )
        ).mappings().first()

    @staticmethod
    def delete_notification(session, notification_id):
        session.execute(
            text("DELETE FROM notifications WHERE id = :notification_id"),
            {"notification_id": notification_id},
        )
        session.commit()


class NotificationComposeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tạo thông báo mobile")
        self.setMinimumWidth(640)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_label = QLabel("Tạo thông báo cho Hội viên / PT")
        title_label.setObjectName("sectionLabel")
        layout.addWidget(title_label)

        description = QLabel(
            "Thông báo được lưu vào database và gửi realtime tới Flutter khi backend đang chạy."
        )
        description.setObjectName("mutedLabel")
        description.setWordWrap(True)
        layout.addWidget(description)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        self.audience_combo = QComboBox()
        self.audience_combo.addItem("Tất cả hội viên và PT", "all_mobile")
        self.audience_combo.addItem("Tất cả hội viên", "members")
        self.audience_combo.addItem("Tất cả PT", "trainers")
        self.audience_combo.addItem("Một tài khoản cụ thể", "specific")
        form.addRow("Đối tượng nhận", self.audience_combo)

        self.user_combo = QComboBox()
        self.user_combo.setEnabled(False)
        form.addRow("Tài khoản cụ thể", self.user_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Thông báo chung", "announcement")
        self.type_combo.addItem("Lịch tập / lịch dạy", "schedule")
        self.type_combo.addItem("Gói tập / số buổi", "membership")
        self.type_combo.addItem("Thanh toán", "payment")
        self.type_combo.addItem("Khuyến mãi", "promotion")
        self.type_combo.addItem("Bảo trì hệ thống", "maintenance")
        self.type_combo.addItem("Nhắc nhở", "reminder")
        self.type_combo.addItem("Hệ thống", "system")
        form.addRow("Loại thông báo", self.type_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItem("Bình thường", "normal")
        self.priority_combo.addItem("Quan trọng", "high")
        self.priority_combo.addItem("Khẩn", "urgent")
        form.addRow("Mức độ", self.priority_combo)

        self.route_combo = QComboBox()
        self.route_combo.addItem("Không điều hướng", "")
        self.route_combo.addItem("Màn hình thông báo", "/notifications")
        self.route_combo.addItem("Lịch tập / lịch dạy", "/schedule")
        self.route_combo.addItem("Gói tập", "/membership")
        self.route_combo.addItem("Lịch sử check-in", "/history")
        self.route_combo.addItem("Hồ sơ", "/profile")
        form.addRow("Mở màn hình", self.route_combo)

        self.title_input = QLineEdit()
        self.title_input.setMaxLength(200)
        self.title_input.setPlaceholderText("Ví dụ: Phòng gym đóng cửa bảo trì sáng Chủ nhật")
        form.addRow("Tiêu đề", self.title_input)

        self.body_input = QTextEdit()
        self.body_input.setMinimumHeight(130)
        self.body_input.setPlaceholderText(
            "Nhập nội dung rõ ràng, có ngày giờ và hướng dẫn cụ thể cho người nhận."
        )
        form.addRow("Nội dung", self.body_input)

        layout.addLayout(form)

        self.recipient_hint = QLabel("Đang tính số người nhận...")
        self.recipient_hint.setObjectName("mutedLabel")
        layout.addWidget(self.recipient_hint)

        buttons = QDialogButtonBox()
        self.btn_send = buttons.addButton("Gửi thông báo", QDialogButtonBox.ButtonRole.AcceptRole)
        self.btn_send.setObjectName("primaryButton")
        self.btn_cancel = buttons.addButton("Hủy", QDialogButtonBox.ButtonRole.RejectRole)
        self.btn_cancel.setObjectName("secondaryButton")
        layout.addWidget(buttons)

        self.audience_combo.currentIndexChanged.connect(self._audience_changed)
        self.user_combo.currentIndexChanged.connect(self._update_recipient_hint)
        self.btn_send.clicked.connect(self.send_notification)
        self.btn_cancel.clicked.connect(self.reject)

        self._load_users()
        self._audience_changed()

    def _load_users(self):
        session = get_session()
        try:
            users = NotificationRepository.list_mobile_users(session)
        finally:
            session.close()

        self.user_combo.clear()
        for item in users:
            label = f"{item['full_name']} · {item['role_display']} · @{item['username']}"
            self.user_combo.addItem(label, int(item["id"]))

    def _audience_changed(self):
        self.user_combo.setEnabled(self.audience_combo.currentData() == "specific")
        self._update_recipient_hint()

    def _update_recipient_hint(self):
        session = get_session()
        try:
            targets = NotificationRepository.target_users(
                session,
                self.audience_combo.currentData(),
                self.user_combo.currentData(),
            )
        finally:
            session.close()
        self.recipient_hint.setText(f"Dự kiến gửi tới {len(targets)} tài khoản mobile đang hoạt động.")

    def send_notification(self):
        if not is_admin():
            QMessageBox.warning(self, "Không có quyền", "Chỉ Admin được tạo thông báo.")
            return

        title = self.title_input.text().strip()
        body = self.body_input.toPlainText().strip()
        if not title:
            QMessageBox.warning(self, "Thiếu tiêu đề", "Vui lòng nhập tiêu đề thông báo.")
            self.title_input.setFocus()
            return
        if len(body) < 5:
            QMessageBox.warning(self, "Thiếu nội dung", "Nội dung thông báo phải có ít nhất 5 ký tự.")
            self.body_input.setFocus()
            return

        session = get_session()
        try:
            targets = NotificationRepository.target_users(
                session,
                self.audience_combo.currentData(),
                self.user_combo.currentData(),
            )
            if not targets:
                QMessageBox.warning(self, "Không có người nhận", "Không tìm thấy tài khoản phù hợp.")
                return

            answer = QMessageBox.question(
                self,
                "Xác nhận gửi",
                f"Gửi thông báo này tới {len(targets)} tài khoản?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

            sent_targets = NotificationRepository.send(
                session,
                audience=self.audience_combo.currentData(),
                specific_user_id=self.user_combo.currentData(),
                notification_type=self.type_combo.currentData(),
                title=title,
                body=body,
                priority=self.priority_combo.currentData(),
                route=self.route_combo.currentData(),
            )
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Gửi thất bại", f"Không thể tạo thông báo:\n{exc}")
            return
        finally:
            session.close()

        QMessageBox.information(
            self,
            "Đã gửi",
            f"Đã tạo thành công {len(sent_targets)} thông báo.\n"
            "Flutter sẽ nhận realtime nếu backend FastAPI đang chạy.",
        )
        self.accept()


class TabNotifications(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(
            page_title(
                "Quản lý thông báo",
                "Tạo thông báo cho Hội viên/PT và theo dõi trạng thái đã đọc",
            )
        )

        toolbar = QFrame()
        toolbar.setObjectName("panel")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm người nhận, username hoặc tiêu đề")
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tất cả loại", "all")
        for label, value in (
            ("Thông báo chung", "announcement"),
            ("Lịch tập", "schedule"),
            ("Gói tập", "membership"),
            ("Thanh toán", "payment"),
            ("Khuyến mãi", "promotion"),
            ("Bảo trì", "maintenance"),
            ("Nhắc nhở", "reminder"),
            ("Hệ thống", "system"),
            ("Check-in", "checkin"),
            ("KPI PT", "kpi"),
        ):
            self.type_filter.addItem(label, value)

        self.btn_search = QPushButton("Tìm kiếm")
        self.btn_search.setObjectName("secondaryButton")
        self.btn_reload = QPushButton("↻")
        self.btn_reload.setObjectName("iconButton")
        self.btn_reload.setToolTip("Tải lại thông báo")
        self.btn_create = QPushButton("Tạo thông báo")
        self.btn_create.setObjectName("primaryButton")

        toolbar_layout.addWidget(self.search_input, 1)
        toolbar_layout.addWidget(self.type_filter)
        toolbar_layout.addWidget(self.btn_search)
        toolbar_layout.addWidget(self.btn_reload)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_create)
        layout.addWidget(toolbar)

        stats_layout = QHBoxLayout()
        self.sent_today_card = self._stat_card("Đã gửi hôm nay", "0")
        self.unread_card = self._stat_card("Chưa đọc", "0")
        self.recipient_card = self._stat_card("Tài khoản đã nhận", "0")
        self.total_card = self._stat_card("Tổng thông báo", "0")
        stats_layout.addWidget(self.sent_today_card["frame"])
        stats_layout.addWidget(self.unread_card["frame"])
        stats_layout.addWidget(self.recipient_card["frame"])
        stats_layout.addWidget(self.total_card["frame"])
        layout.addLayout(stats_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Người nhận", "Vai trò", "Loại", "Tiêu đề", "Trạng thái", "Thời gian"]
        )
        configure_table(self.table)
        self.table.setColumnWidth(0, 70)
        self.table.setColumnWidth(1, 190)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 360)
        self.table.setColumnWidth(5, 100)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        note = QLabel("Mẹo: nháy đúp một dòng để xem đầy đủ nội dung trong database/API Flutter.")
        note.setObjectName("mutedLabel")
        self.btn_delete = QPushButton("Xóa thông báo đã chọn")
        self.btn_delete.setObjectName("dangerButton")
        actions.addWidget(note)
        actions.addStretch()
        actions.addWidget(self.btn_delete)
        layout.addLayout(actions)

        self.btn_create.clicked.connect(self.open_compose_dialog)
        self.btn_search.clicked.connect(self.refresh)
        self.btn_reload.clicked.connect(self.refresh)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.search_input.returnPressed.connect(self.refresh)
        self.type_filter.currentIndexChanged.connect(self.refresh)

        if not is_admin():
            self.btn_create.setEnabled(False)
            self.btn_delete.setEnabled(False)

        self.refresh()

    @staticmethod
    def _stat_card(caption, value):
        frame = QFrame()
        frame.setObjectName("statCard")
        card_layout = QVBoxLayout(frame)
        card_layout.setContentsMargins(16, 14, 16, 14)
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        caption_label = QLabel(caption)
        caption_label.setObjectName("statCaption")
        card_layout.addWidget(value_label)
        card_layout.addWidget(caption_label)
        return {"frame": frame, "value": value_label}

    def open_compose_dialog(self):
        dialog = NotificationComposeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def refresh(self):
        session = get_session()
        try:
            rows = NotificationRepository.list_recent(
                session,
                search_text=self.search_input.text().strip(),
                notification_type=self.type_filter.currentData(),
            )
            stats = NotificationRepository.statistics(session) or {}
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Không tải được thông báo",
                "Hãy kiểm tra đã import database gym_db_full_api.sql hay chưa.\n\n"
                f"Chi tiết: {exc}",
            )
            return
        finally:
            session.close()

        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            created_at = row["created_at"]
            created_text = (
                created_at.strftime("%d/%m/%Y %H:%M")
                if isinstance(created_at, datetime)
                else str(created_at or "")
            )
            values = [
                row["id"],
                row["recipient_name"],
                row["role_display"] or "",
                row["type"],
                row["title"],
                "Đã đọc" if row["is_read"] else "Chưa đọc",
                created_text,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column in (0, 5):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_index, column, item)

        self.sent_today_card["value"].setText(str(int(stats.get("sent_today") or 0)))
        self.unread_card["value"].setText(str(int(stats.get("unread_total") or 0)))
        self.recipient_card["value"].setText(str(int(stats.get("recipient_total") or 0)))
        self.total_card["value"].setText(str(int(stats.get("notification_total") or 0)))

    def selected_notification_id(self):
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            return None
        return int(self.table.item(row, 0).text())

    def delete_selected(self):
        if not is_admin():
            QMessageBox.warning(self, "Không có quyền", "Chỉ Admin được xóa thông báo.")
            return
        notification_id = self.selected_notification_id()
        if notification_id is None:
            QMessageBox.information(self, "Chưa chọn", "Hãy chọn một thông báo trong bảng.")
            return
        answer = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Xóa thông báo đã chọn khỏi tài khoản người nhận?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        session = get_session()
        try:
            NotificationRepository.delete_notification(session, notification_id)
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Xóa thất bại", str(exc))
        finally:
            session.close()
        self.refresh()
