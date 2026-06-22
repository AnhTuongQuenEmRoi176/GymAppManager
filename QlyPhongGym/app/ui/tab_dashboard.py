import os
import time
import uuid
from datetime import date, datetime

import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
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
from app.models import Checkin, Member, MemberPackage, Package, PTSession, QRDemo, Trainer
from app.state import get_current_user
from app.ui.confirm_session import ConfirmSessionDialog
from app.ui.theme import page_title
from app.utils.camera_worker import CameraWorker


class TabDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.last_seen = {}
        self.pending_entities = None
        self.pending_photo = None
        self.pending_payloads = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(page_title("Trang chủ quét QR", "Kiểm tra hội viên, PT và xác nhận buổi tập"))

        toolbar = QFrame()
        toolbar.setObjectName("panel")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)
        toolbar_layout.addWidget(QLabel("Chế độ"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Thủ công", "Tự động"])
        toolbar_layout.addWidget(self.mode_combo)
        toolbar_layout.addStretch()
        self.status_label = QLabel("Sẵn sàng quét")
        self.status_label.setObjectName("mutedLabel")
        toolbar_layout.addWidget(self.status_label)
        layout.addWidget(toolbar)

        content = QHBoxLayout()
        content.setSpacing(16)

        camera_panel = QFrame()
        camera_panel.setObjectName("panel")
        camera_layout = QVBoxLayout(camera_panel)
        camera_layout.setContentsMargins(16, 16, 16, 16)
        camera_layout.setSpacing(12)
        camera_layout.addWidget(QLabel("Camera"))

        self.video_frame = QLabel("Camera chưa bật")
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setMinimumSize(680, 420)
        self.video_frame.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8;")
        camera_layout.addWidget(self.video_frame, 1)

        camera_buttons = QHBoxLayout()
        self.btn_on = QPushButton("Bật camera")
        self.btn_on.setObjectName("primaryButton")
        self.btn_off = QPushButton("Tắt camera")
        self.btn_off.setEnabled(False)
        camera_buttons.addWidget(self.btn_on)
        camera_buttons.addWidget(self.btn_off)
        camera_buttons.addStretch()
        camera_layout.addLayout(camera_buttons)
        content.addWidget(camera_panel, 2)

        info_panel = QGroupBox("Thông tin check-in")
        info_panel.setMinimumWidth(360)
        info_layout = QVBoxLayout(info_panel)
        info_layout.setSpacing(14)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(150, 150)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8;")
        self.avatar_label.setText("Ảnh")
        info_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.info = QLabel("Đưa mã QR vào camera để hiển thị thông tin hội viên hoặc PT.")
        self.info.setWordWrap(True)
        self.info.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info.setMinimumHeight(160)
        info_layout.addWidget(self.info)

        self.btn_confirm = QPushButton("Xác nhận check-in")
        self.btn_confirm.setObjectName("primaryButton")
        self.btn_confirm.setVisible(False)
        info_layout.addWidget(self.btn_confirm)
        info_layout.addStretch()
        content.addWidget(info_panel, 1)

        layout.addLayout(content, 1)

        self.btn_confirm.clicked.connect(self.handle_confirm)
        self.btn_on.clicked.connect(self.start_camera)
        self.btn_off.clicked.connect(self.stop_camera)

    def start_camera(self):
        if self.worker and self.worker.isRunning():
            return
        self.worker = CameraWorker(camera_index=0, fps=12)
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

    def _member_summary(self, session, member):
        member_package = (
            session.query(MemberPackage)
            .filter(MemberPackage.member_id == member.id, MemberPackage.end_date >= date.today())
            .order_by(MemberPackage.created_at.desc())
            .first()
        )
        package_info = "Không có gói đang hoạt động"
        trainer_info = "Chưa gán PT"
        if member_package:
            package = session.query(Package).filter(Package.id == member_package.package_id).first()
            if package:
                package_info = f"{package.name} - {member_package.sessions_remaining or 0} buổi còn lại"
            if member_package.pt_id:
                trainer = session.query(Trainer).filter(Trainer.id == member_package.pt_id).first()
                if trainer and trainer.user:
                    trainer_info = trainer.user.full_name
        return package_info, trainer_info

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

        now = datetime.utcnow().timestamp()
        entities = {"member": None, "trainer": None}
        session = get_session()
        try:
            for decoded in decoded_list:
                payload = decoded.get("data")
                if not payload:
                    continue
                last = self.last_seen.get(payload, 0)
                if now - last < 3:
                    continue
                self.last_seen[payload] = now
                try:
                    self._load_payload(session, payload, entities)
                except Exception:
                    continue

            if entities["member"] or entities["trainer"]:
                resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "checkins")
                os.makedirs(resources_dir, exist_ok=True)
                bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
                filename = f"chk_{int(time.time())}_{uuid.uuid4().hex}.jpg"
                filepath = os.path.join(resources_dir, filename)
                cv2.imwrite(filepath, bgr)

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

                if self.mode_combo.currentText() == "Tự động" and not (entities["member"] and entities["trainer"]):
                    self.handle_confirm()
        finally:
            session.close()

    def handle_confirm(self):
        if not self.pending_entities:
            return

        session = get_session()
        try:
            current_user = get_current_user()
            pending_member = self.pending_entities.get("member")
            pending_trainer = self.pending_entities.get("trainer")
            member_id = pending_member.id if pending_member else None
            trainer_id = pending_trainer.id if pending_trainer else None

            member = session.query(Member).filter(Member.id == member_id).first() if member_id else None
            trainer = session.query(Trainer).filter(Trainer.id == trainer_id).first() if trainer_id else None

            if member and trainer and self.mode_combo.currentText() == "Thủ công":
                dialog = ConfirmSessionDialog(trainer, member)
                if dialog.exec() != dialog.DialogCode.Accepted:
                    return

            if member:
                payload_member = next((p for p in self.pending_payloads if p.startswith("member:")), "")
                session.add(
                    Checkin(
                        member_id=member.id,
                        trainer_id=None,
                        scanned_at=datetime.now(),
                        scanner_user_id=current_user.id if current_user else None,
                        source="camera",
                        qr_payload=payload_member,
                        photo=self.pending_photo,
                    )
                )

            if trainer:
                payload_trainer = next((p for p in self.pending_payloads if p.startswith("trainer:")), "")
                session.add(
                    Checkin(
                        member_id=None,
                        trainer_id=trainer.id,
                        scanned_at=datetime.now(),
                        scanner_user_id=current_user.id if current_user else None,
                        source="camera",
                        qr_payload=payload_trainer,
                        photo=self.pending_photo,
                    )
                )

            if member and trainer:
                session.add(
                    PTSession(
                        trainer_id=trainer.id,
                        member_id=member.id,
                        session_date=datetime.now(),
                        confirmed_by=current_user.id if current_user else None,
                    )
                )
                member_package = (
                    session.query(MemberPackage)
                    .filter(
                        MemberPackage.member_id == member.id,
                        MemberPackage.end_date >= date.today(),
                        MemberPackage.sessions_remaining != None,
                    )
                    .order_by(MemberPackage.created_at.desc())
                    .first()
                )
                if member_package and member_package.sessions_remaining and member_package.sessions_remaining > 0:
                    member_package.sessions_remaining -= 1

            session.commit()
            self.info.setText("Check-in đã được lưu thành công.")
            self.status_label.setText("Đã xác nhận")
            self.btn_confirm.setVisible(False)

            for payload in self.pending_payloads:
                self.last_seen.pop(payload, None)
            self.pending_entities = None
            self.pending_photo = None
            self.pending_payloads = []
            QMessageBox.information(self, "Thành công", "Lưu check-in thành công")
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Xác nhận thất bại: {exc}")
        finally:
            session.close()
