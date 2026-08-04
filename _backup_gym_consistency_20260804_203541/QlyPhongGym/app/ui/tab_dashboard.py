import hashlib
import os
import time
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from sqlalchemy import or_, text

from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from app.db import get_session
from app.models import (
    Checkin,
    Member,
    MemberPackage,
    Notification,
    Package,
    PTSession,
    QRDemo,
    Trainer,
    TrainingSchedule,
)
from app.state import get_current_user, is_admin
try:
    from app.ui.tab_notifications import NotificationComposeDialog
except ImportError:
    NotificationComposeDialog = None
from app.ui.confirm_session import ConfirmSessionDialog
from app.ui.theme import page_title

class TabDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.last_seen = {}
        self.pending_entities = None
        self.pending_photo = None
        self.pending_payloads = []
        self.pending_mobile_qr = {"member": None, "trainer": None}
        self.confirming = False
        self.auto_pause_until = 0
        self.last_auto_confirm = {}
        self.scan_clear_deadline = 0
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(page_title("Trang chủ quét QR", "Kiểm tra hội viên, PT và xác nhận buổi tập"))
        toolbar = QFrame()
        toolbar.setObjectName("panel")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 12, 16, 12)
        toolbar_layout.addWidget(QLabel("Chế độ"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Thủ công", "Tự động"])
        toolbar_layout.addWidget(self.mode_combo)
        toolbar_layout.addStretch()
        if is_admin() and NotificationComposeDialog is not None:
            self.btn_create_notification = QPushButton("Tạo thông báo")
            self.btn_create_notification.setObjectName("primaryButton")
            self.btn_create_notification.clicked.connect(self.open_notification_dialog)
            toolbar_layout.addWidget(self.btn_create_notification)
        self.status_label = QLabel("Sẵn sàng quét")
        self.status_label.setObjectName("mutedLabel")
        toolbar_layout.addWidget(self.status_label)
        layout.addWidget(toolbar)
        content = QHBoxLayout()
        content.setSpacing(14)

        camera_panel = QFrame()
        camera_panel.setObjectName("panel")
        camera_layout = QVBoxLayout(camera_panel)
        camera_layout.setContentsMargins(16, 16, 16, 16)
        camera_layout.setSpacing(10)
        title = QLabel("Camera")
        title.setObjectName("sectionLabel")
        camera_layout.addWidget(title)
        self.video_frame = QLabel("Camera chưa bật")
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setMinimumSize(620, 380)
        self.video_frame.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8;")
        camera_layout.addWidget(self.video_frame, 1)
        camera_buttons = QHBoxLayout()
        self.btn_on = QPushButton("Bật camera")
        self.btn_on.setObjectName("successButton")
        self.btn_off = QPushButton("Tắt camera")
        self.btn_off.setObjectName("dangerButton")
        self.btn_off.setEnabled(False)
        camera_buttons.addWidget(self.btn_on)
        camera_buttons.addWidget(self.btn_off)
        camera_buttons.addStretch()
        camera_layout.addLayout(camera_buttons)
        content.addWidget(camera_panel, 2)
        info_panel = QGroupBox("Thông tin check-in")
        info_panel.setMinimumWidth(340)
        info_layout = QVBoxLayout(info_panel)
        info_layout.setSpacing(12)
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(140, 140)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8;")
        self.avatar_label.setText("Ảnh")
        info_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.info = QLabel("Đưa mã QR vào camera để hiển thị thông tin hội viên hoặc PT.")
        self.info.setWordWrap(True)
        self.info.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info.setMinimumHeight(150)
        info_layout.addWidget(self.info)
        self.btn_confirm = QPushButton("Xác nhận check-in")
        self.btn_confirm.setObjectName("primaryButton")
        self.btn_confirm.setVisible(False)
        info_layout.addWidget(self.btn_confirm)
        self.btn_reject = QPushButton("Từ chối")
        self.btn_reject.setObjectName("dangerButton")
        self.btn_reject.setVisible(False)
        info_layout.addWidget(self.btn_reject)
        info_layout.addStretch()
        content.addWidget(info_panel, 1)

        layout.addLayout(content, 1)
        self.btn_confirm.clicked.connect(lambda: self.handle_confirm(show_message=True))
        self.btn_reject.clicked.connect(self.clear_scan_state)
        self.btn_on.clicked.connect(self.start_camera)
        self.btn_off.clicked.connect(self.stop_camera)

    def open_notification_dialog(self):
        if NotificationComposeDialog is None:
            QMessageBox.warning(
                self,
                "Chưa có module thông báo",
                "Không tìm thấy app.ui.tab_notifications.",
            )
            return
        dialog = NotificationComposeDialog(self)
        dialog.exec()

    def start_camera(self):
        if self.worker and self.worker.isRunning():
            return
        from app.utils.camera_worker import CameraWorker
        self.worker = CameraWorker(camera_index=0, fps=10)
        self.worker.frame_ready.connect(self.on_frame)
        self.worker.start()
        self.btn_on.setEnabled(False)
        self.btn_off.setEnabled(True)
        self.status_label.setText("Camera đang chạy")

    def stop_camera(self):
        if self.worker:
            self.worker.stop()
        self.btn_on.setEnabled(True)
        self.btn_off.setEnabled(False)
        self.status_label.setText("Camera đã tắt")
    def _set_avatar(self, path):
        if path and os.path.isfile(path):
            pix = QPixmap(path).scaled(
                self.avatar_label.width(),
                self.avatar_label.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.avatar_label.setPixmap(pix)
        else:
            self.avatar_label.setPixmap(QPixmap())
            self.avatar_label.setText("Ảnh")
    @staticmethod
    def _active_status_filter():
        # Rows created by an older Windows build may have NULL/blank status.
        return or_(
            MemberPackage.status == "active",
            MemberPackage.status.is_(None),
            MemberPackage.status == "",
        )

    def _active_package_rows(self, session, member_id, lock=False):
        query = (
            session.query(MemberPackage, Package)
            .join(Package, Package.id == MemberPackage.package_id)
            .filter(
                MemberPackage.member_id == member_id,
                self._active_status_filter(),
                MemberPackage.start_date <= date.today(),
                MemberPackage.end_date >= date.today(),
            )
            .order_by(
                MemberPackage.start_date.desc(),
                MemberPackage.id.desc(),
            )
        )
        if lock:
            query = query.with_for_update()
        return query.all()

    def _find_active_package(
        self,
        session,
        member_id,
        package_types,
        *,
        trainer_id=None,
        lock=False,
    ):
        package_types = {str(item).upper() for item in package_types}
        for member_package, package in self._active_package_rows(
            session, member_id, lock=lock
        ):
            current_type = str(package.package_type or "GYM").upper()
            if current_type not in package_types:
                continue
            if trainer_id is not None and member_package.pt_id != trainer_id:
                continue
            return member_package, package
        return None

    @staticmethod
    def _effective_sessions_total(member_package, package):
        if member_package.sessions_total is not None:
            return int(member_package.sessions_total)
        if member_package.sessions_remaining is not None:
            return int(member_package.sessions_remaining)
        if package.sessions is not None:
            return int(package.sessions)
        return None

    @classmethod
    def _effective_sessions_remaining(cls, member_package, package):
        if member_package.sessions_remaining is not None:
            return int(member_package.sessions_remaining)
        return cls._effective_sessions_total(member_package, package)

    @classmethod
    def _remaining_text(cls, member_package, package):
        package_type = str(package.package_type or "GYM").upper()
        remaining = cls._effective_sessions_remaining(member_package, package)
        if remaining is None:
            return "Không giới hạn"
        unit = "buổi PT" if package_type in {"PT", "COMBO"} else "lượt tập"
        return f"{remaining} {unit} còn lại"

    def _member_summary(self, session, member):
        rows = self._active_package_rows(session, member.id)
        base_row = next(
            (row for row in rows if str(row[1].package_type or "GYM").upper() in {"GYM", "COMBO"}),
            rows[0] if rows else None,
        )
        pt_row = next(
            (
                row
                for row in rows
                if str(row[1].package_type or "GYM").upper() in {"PT", "COMBO"}
                and row[0].pt_id is not None
            ),
            None,
        )

        if base_row is None:
            return "Không có gói đang hoạt động", "Chưa gán PT"

        base_membership, base_package = base_row
        lines = [
            f"{base_package.name} - {self._remaining_text(base_membership, base_package)}"
        ]
        if pt_row and pt_row[0].id != base_membership.id:
            lines.append(
                f"{pt_row[1].name} - {self._remaining_text(pt_row[0], pt_row[1])}"
            )

        trainer_info = "Chưa gán PT"
        trainer_id = pt_row[0].pt_id if pt_row else base_membership.pt_id
        if trainer_id:
            trainer = session.query(Trainer).filter(Trainer.id == trainer_id).first()
            if trainer and trainer.user:
                trainer_info = trainer.user.full_name or trainer.user.username
        return "\n".join(lines), trainer_info

    # MOBILE_QR_COMPATIBILITY_PATCH_V1
    def _load_mobile_qr(self, session, payload, entities):
        """Nhận QR động do Flutter/FastAPI sinh qua bảng qr_tokens."""
        # Token hiện tại là JWT: ba phần ngăn bởi hai dấu chấm.
        if len(payload) < 80 or payload.count(".") != 2:
            return False

        token_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        try:
            record = session.execute(
                text(
                    """
                    SELECT token_id, entity_type, entity_id, expires_at, used_at
                    FROM qr_tokens
                    WHERE token_hash = :token_hash
                    LIMIT 1
                    """
                ),
                {"token_hash": token_hash},
            ).mappings().first()
        except Exception as exc:
            raise RuntimeError(
                "Database chưa có bảng qr_tokens. Hãy dùng gym_db_full_api.sql."
            ) from exc

        if record is None:
            raise ValueError("Mã QR mobile không tồn tại hoặc không thuộc hệ thống này.")
        if record["used_at"] is not None:
            raise ValueError("Mã QR mobile đã được sử dụng.")
        if record["expires_at"] <= datetime.now():
            raise ValueError("Mã QR mobile đã hết hạn. Hãy mở mã mới trên Flutter.")

        entity_type = str(record["entity_type"]).strip().lower()
        if entity_type not in {"member", "trainer"}:
            raise ValueError("Loại QR mobile không hợp lệ.")

        self._load_payload(
            session,
            f"{entity_type}:{int(record['entity_id'])}",
            entities,
        )
        if entities.get(entity_type) is None:
            raise ValueError("Không tìm thấy hồ sơ tương ứng với QR mobile.")

        self.pending_mobile_qr[entity_type] = {
            "token_hash": token_hash,
            "token_id": str(record["token_id"]),
        }
        self.info.setText(
            self.info.text() + "\nNguồn QR: Ứng dụng Flutter (mã động)"
        )
        return True

    def _consume_mobile_qr_tokens(self, session, scanner_user_id):
        """Đánh dấu QR động đã dùng ngay trong cùng transaction check-in."""
        for entity_type, record in self.pending_mobile_qr.items():
            if not record:
                continue
            result = session.execute(
                text(
                    """
                    UPDATE qr_tokens
                    SET used_at = NOW(), used_by = :used_by
                    WHERE token_hash = :token_hash
                      AND entity_type = :entity_type
                      AND used_at IS NULL
                      AND expires_at > NOW()
                    """
                ),
                {
                    "used_by": scanner_user_id,
                    "token_hash": record["token_hash"],
                    "entity_type": entity_type,
                },
            )
            if result.rowcount != 1:
                raise ValueError(
                    f"QR {entity_type} đã hết hạn hoặc vừa được sử dụng ở thiết bị khác."
                )

    def _checkin_qr_payload(self, entity_type):
        mobile = self.pending_mobile_qr.get(entity_type)
        if mobile:
            return mobile["token_id"]
        return next(
            (p for p in self.pending_payloads if p.startswith(f"{entity_type}:")),
            "",
        )

    def _load_payload(self, session, payload, entities):
        if payload.startswith("member:"):
            member_id = int(payload.split(":", 1)[1])
            member = session.query(Member).filter(Member.id == member_id).first()
            if member:
                entities["member"] = member
                self.pending_payloads.append(payload)
                package_info, trainer_info = self._member_summary(session, member)
                self.info.setText(
                    f"Hội viên: {member.user.full_name}\n"
                    f"SĐT: {member.user.phone or 'N/A'}\n"
                    f"Gói tập: {package_info}\n"
                    f"PT phụ trách: {trainer_info}"
                )
                self._set_avatar(member.user.avatar)
        elif payload.startswith("trainer:"):
            trainer_id = int(payload.split(":", 1)[1])
            trainer = session.query(Trainer).filter(Trainer.id == trainer_id).first()
            if trainer:
                entities["trainer"] = trainer
                self.pending_payloads.append(payload)
                self.info.setText(
                    f"PT: {trainer.user.full_name}\n"
                    f"SĐT: {trainer.user.phone or 'N/A'}\n"
                    f"Bộ môn: {trainer.specialty or 'Chưa cập nhật'}"
                )
                self._set_avatar(trainer.user.avatar)
        else:
            if self._load_mobile_qr(session, payload, entities):
                return
            demo = session.query(QRDemo).filter(QRDemo.code == payload).first()
            if demo:
                self._load_payload(session, f"{demo.entity_type}:{demo.entity_id}", entities)
    def on_frame(self, rgb_frame, decoded_list):
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(image).scaled(
            self.video_frame.width(),
            self.video_frame.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.video_frame.setPixmap(pix)
        if not decoded_list:
            return

        now = time.monotonic()
        if self.confirming or self.pending_entities or now < self.auto_pause_until:
            return
        entities = {"member": None, "trainer": None}
        session = get_session()
        try:
            for decoded in decoded_list:
                payload = decoded.get("data")
                if not payload:
                    continue
                last = self.last_seen.get(payload, 0)
                cooldown = 12 if self.mode_combo.currentText() == "Tự động" else 4
                if now - last < cooldown:
                    continue
                self.last_seen[payload] = now
                try:
                    self._load_payload(session, payload, entities)
                except Exception as exc:
                    message = str(exc) or "Không đọc được nội dung QR."
                    self.status_label.setText("QR không hợp lệ")
                    self.info.setText(message)
                    continue
            if entities["member"] or entities["trainer"]:
                resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "checkins")
                os.makedirs(resources_dir, exist_ok=True)
                try:
                    import cv2
                    bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
                    filename = f"chk_{int(time.time())}_{uuid.uuid4().hex}.jpg"
                    filepath = os.path.join(resources_dir, filename)
                    cv2.imwrite(filepath, bgr)
                except Exception:
                    filepath = None

                self.pending_entities = entities
                self.pending_photo = filepath
                detected = []
                if entities["member"]:
                    detected.append("hội viên")
                if entities["trainer"]:
                    detected.append("PT")
                self.status_label.setText("Phát hiện: " + " + ".join(detected))
                if entities["member"] and entities["trainer"]:
                    self.btn_confirm.setText("Xác nhận buổi tập")
                else:
                    self.btn_confirm.setText("Xác nhận check-in")
                self.btn_confirm.setVisible(True)
                self.btn_reject.setVisible(True)
                self.schedule_scan_clear()
                if self.mode_combo.currentText() == "Tự động" and not (entities["member"] and entities["trainer"]):
                    self.handle_confirm(show_message=False, automatic=True)
        finally:
            session.close()

    def handle_confirm(self, show_message=True, automatic=False):
        if not self.pending_entities or self.confirming:
            return

        self.confirming = True
        session = get_session()
        try:
            current_user = get_current_user()
            scanner_user_id = current_user.id if current_user else None
            pending_member = self.pending_entities.get("member")
            pending_trainer = self.pending_entities.get("trainer")
            member_id = pending_member.id if pending_member else None
            trainer_id = pending_trainer.id if pending_trainer else None
            member = (
                session.query(Member).filter(Member.id == member_id).first()
                if member_id
                else None
            )
            trainer = (
                session.query(Trainer).filter(Trainer.id == trainer_id).first()
                if trainer_id
                else None
            )

            if member and trainer and self.mode_combo.currentText() == "Thủ công":
                dialog = ConfirmSessionDialog(trainer, member)
                if dialog.exec() != dialog.DialogCode.Accepted:
                    return

            now = datetime.now()
            pair_group_id = str(uuid.uuid4()) if member and trainer else None
            gym_membership = None
            pt_membership = None
            pt_package = None

            # Validate and lock the exact counter before consuming one-time QR tokens.
            if member and trainer:
                result = self._find_active_package(
                    session,
                    member.id,
                    {"PT", "COMBO"},
                    trainer_id=trainer.id,
                    lock=True,
                )
                if result is None:
                    raise ValueError(
                        "Hội viên không có gói PT/COMBO còn hiệu lực với PT này."
                    )
                pt_membership, pt_package = result
                pt_remaining = self._effective_sessions_remaining(
                    pt_membership, pt_package
                )
                if pt_remaining is None:
                    raise ValueError("Gói PT/COMBO không có số buổi để trừ.")
                if pt_remaining <= 0:
                    raise ValueError("Hội viên đã hết số buổi PT.")
                if pt_membership.sessions_total is None:
                    pt_membership.sessions_total = self._effective_sessions_total(
                        pt_membership, pt_package
                    )
                if pt_membership.sessions_remaining is None:
                    pt_membership.sessions_remaining = pt_remaining
            elif member:
                result = self._find_active_package(
                    session, member.id, {"GYM", "COMBO"}, lock=True
                )
                if result is None:
                    raise ValueError("Hội viên không có gói GYM/COMBO còn hiệu lực.")
                gym_membership, gym_package = result
                # A finite GYM package is decremented on member-only check-in.
                if str(gym_package.package_type or "GYM").upper() == "GYM":
                    gym_remaining = self._effective_sessions_remaining(
                        gym_membership, gym_package
                    )
                    if gym_remaining is not None and gym_remaining <= 0:
                        raise ValueError("Gói GYM đã hết lượt check-in.")
                    if gym_membership.sessions_total is None:
                        gym_membership.sessions_total = self._effective_sessions_total(
                            gym_membership, gym_package
                        )
                    if (
                        gym_membership.sessions_remaining is None
                        and gym_remaining is not None
                    ):
                        gym_membership.sessions_remaining = gym_remaining

            self._consume_mobile_qr_tokens(session, scanner_user_id)

            if member:
                payload_member = self._checkin_qr_payload("member")
                session.add(
                    Checkin(
                        member_id=member.id,
                        trainer_id=None,
                        scanned_at=now,
                        scanner_user_id=scanner_user_id,
                        source="QR Mobile" if self.pending_mobile_qr.get("member") else "camera",
                        qr_payload=payload_member,
                        photo=self.pending_photo,
                        status="confirmed",
                        confirmed_at=now,
                        pair_group_id=pair_group_id,
                        device_id="WINDOWS-CAMERA",
                        location="Quầy check-in chính",
                    )
                )

            if trainer:
                payload_trainer = self._checkin_qr_payload("trainer")
                session.add(
                    Checkin(
                        member_id=None,
                        trainer_id=trainer.id,
                        scanned_at=now,
                        scanner_user_id=scanner_user_id,
                        source="QR Mobile" if self.pending_mobile_qr.get("trainer") else "camera",
                        qr_payload=payload_trainer,
                        photo=self.pending_photo,
                        status="confirmed",
                        confirmed_at=now,
                        pair_group_id=pair_group_id,
                        device_id="WINDOWS-CAMERA",
                        location="Quầy check-in chính",
                    )
                )

            if member and trainer:
                pt_membership.sessions_remaining -= 1
                pt_membership.updated_at = now

                nearest_schedule = (
                    session.query(TrainingSchedule)
                    .filter(
                        TrainingSchedule.member_id == member.id,
                        TrainingSchedule.trainer_id == trainer.id,
                        TrainingSchedule.status.in_(["pending", "upcoming"]),
                        TrainingSchedule.start_at >= now - timedelta(hours=12),
                        TrainingSchedule.start_at <= now + timedelta(hours=12),
                    )
                    .order_by(TrainingSchedule.start_at.asc())
                    .with_for_update()
                    .first()
                )
                if nearest_schedule:
                    nearest_schedule.status = "completed"
                    nearest_schedule.updated_at = now

                rate = Decimal(
                    str(trainer.session_commission_percent or Decimal("0.50"))
                )
                commission_base = Decimal(
                    str(pt_membership.price_paid or pt_package.price or 0)
                )
                commission_amount = (
                    commission_base * rate / Decimal("100")
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                session.add(
                    PTSession(
                        trainer_id=trainer.id,
                        member_id=member.id,
                        member_package_id=pt_membership.id,
                        schedule_id=nearest_schedule.id if nearest_schedule else None,
                        session_date=now,
                        confirmed_by=scanner_user_id,
                        status="confirmed",
                        commission_rate=rate,
                        commission_amount=commission_amount,
                        created_at=now,
                    )
                )

                if member.user:
                    session.add(
                        Notification(
                            user_id=member.user.id,
                            type="checkin",
                            title="Buổi tập PT đã được xác nhận",
                            body=(
                                "Hệ thống đã trừ 1 buổi PT. "
                                f"Còn lại {pt_membership.sessions_remaining} buổi."
                            ),
                            data_json={
                                "member_package_id": pt_membership.id,
                                "sessions_remaining": pt_membership.sessions_remaining,
                                "pair_group_id": pair_group_id,
                            },
                            is_read=False,
                            created_at=now,
                        )
                    )
                if trainer.user:
                    session.add(
                        Notification(
                            user_id=trainer.user.id,
                            type="kpi",
                            title="KPI buổi PT đã cập nhật",
                            body="Một buổi PT mới đã được ghi nhận vào KPI.",
                            data_json={
                                "member_package_id": pt_membership.id,
                                "commission_amount": float(commission_amount),
                                "pair_group_id": pair_group_id,
                            },
                            is_read=False,
                            created_at=now,
                        )
                    )
            elif member and gym_membership is not None:
                # Unlimited GYM package keeps NULL. Finite package loses one entry.
                if gym_membership.sessions_remaining is not None:
                    gym_membership.sessions_remaining -= 1
                    gym_membership.updated_at = now
                if member.user:
                    remaining = (
                        "không giới hạn"
                        if gym_membership.sessions_remaining is None
                        else f"{gym_membership.sessions_remaining} lượt"
                    )
                    session.add(
                        Notification(
                            user_id=member.user.id,
                            type="checkin",
                            title="Check-in thành công",
                            body=f"Số lượt gói GYM còn lại: {remaining}.",
                            data_json={
                                "member_package_id": gym_membership.id,
                                "sessions_remaining": gym_membership.sessions_remaining,
                            },
                            is_read=False,
                            created_at=now,
                        )
                    )

            session.commit()
            if automatic:
                self.status_label.setText("Đã tự động lưu check-in")
            else:
                self.info.setText("Check-in đã được lưu và đồng bộ thành công.")
                self.status_label.setText("Đã xác nhận")

            self.btn_confirm.setVisible(False)
            self.btn_reject.setVisible(False)
            QTimer.singleShot(5000, self.clear_scan_state)
            if not automatic:
                for payload in self.pending_payloads:
                    self.last_seen.pop(payload, None)
            else:
                self.auto_pause_until = time.monotonic() + 5
            self.pending_entities = None
            self.pending_photo = None
            self.pending_payloads = []
            self.pending_mobile_qr = {"member": None, "trainer": None}
            if show_message:
                QMessageBox.information(
                    self, "Thành công", "Lưu check-in và cập nhật số buổi thành công"
                )
        except Exception as exc:
            session.rollback()
            if show_message:
                QMessageBox.critical(self, "Lỗi", f"Xác nhận thất bại: {exc}")
            else:
                self.status_label.setText(f"Lỗi auto check-in: {exc}")
        finally:
            session.close()
            self.confirming = False

    def schedule_scan_clear(self):
        self.scan_clear_deadline = time.monotonic() + 5
        QTimer.singleShot(5000, self.clear_scan_if_pending)

    def clear_scan_if_pending(self):
        if self.pending_entities and not self.confirming and time.monotonic() >= self.scan_clear_deadline:
            self.clear_scan_state()
    def clear_scan_state(self):
        self.pending_entities = None
        self.pending_photo = None
        self.pending_payloads = []
        self.pending_mobile_qr = {"member": None, "trainer": None}
        self.btn_confirm.setVisible(False)
        self.btn_reject.setVisible(False)
        self.avatar_label.setPixmap(QPixmap())
        self.avatar_label.setText("Ảnh")
        self.info.setText("Đưa mã QR vào camera để hiển thị thông tin hội viên hoặc PT.")
        self.status_label.setText("Sẵn sàng quét")
        self.auto_pause_until = time.monotonic() + 1
