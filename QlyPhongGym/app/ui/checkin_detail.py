import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout

from app.db import SessionLocal
from app.models import Checkin
from app.ui.theme import page_title


class CheckinDetailDialog(QDialog):
    def __init__(self, checkin_id):
        super().__init__()
        self.setWindowTitle("Chi tiết check-in")
        self.resize(620, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(page_title("Chi tiết check-in", f"Mã lượt quét #{checkin_id}"))

        session = SessionLocal()
        try:
            checkin = session.query(Checkin).filter(Checkin.id == checkin_id).first()
            if not checkin:
                layout.addWidget(QLabel("Check-in không tồn tại"))
                return

            panel = QFrame()
            panel.setObjectName("panel")
            info_layout = QHBoxLayout(panel)
            info_layout.setContentsMargins(16, 16, 16, 16)
            info_layout.setSpacing(16)

            avatar_label = QLabel("Không có ảnh")
            avatar_label.setFixedSize(120, 120)
            avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar_label.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8;")
            avatar_path = None
            if checkin.member and checkin.member.user.avatar:
                avatar_path = checkin.member.user.avatar
            elif checkin.trainer and checkin.trainer.user.avatar:
                avatar_path = checkin.trainer.user.avatar
            if avatar_path and os.path.isfile(avatar_path):
                avatar_label.setPixmap(QPixmap(avatar_path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            info_layout.addWidget(avatar_label)

            details = QVBoxLayout()
            if checkin.member:
                details.addWidget(QLabel(f"Hội viên: {checkin.member.user.full_name}"))
                details.addWidget(QLabel(f"SĐT: {checkin.member.user.phone or 'N/A'}"))
            elif checkin.trainer:
                details.addWidget(QLabel(f"PT: {checkin.trainer.user.full_name}"))
                details.addWidget(QLabel(f"SĐT: {checkin.trainer.user.phone or 'N/A'}"))
            details.addWidget(QLabel(f"Ngày quét: {checkin.scanned_at}"))
            details.addWidget(QLabel(f"Nguồn: {checkin.source or 'N/A'}"))
            details.addWidget(QLabel(f"QR: {checkin.qr_payload or 'N/A'}"))
            info_layout.addLayout(details, 1)
            layout.addWidget(panel)

            if checkin.photo and os.path.isfile(checkin.photo):
                photo_title = QLabel("Ảnh chụp khi quét")
                photo_title.setObjectName("sectionLabel")
                layout.addWidget(photo_title)
                photo_label = QLabel()
                photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                photo_label.setPixmap(QPixmap(checkin.photo).scaled(520, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                layout.addWidget(photo_label)
        finally:
            session.close()
