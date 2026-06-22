import os
from datetime import timedelta

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.db import SessionLocal
from app.models import Checkin, User
from app.ui.theme import page_title


class CheckinDetailDialog(QDialog):
    def __init__(self, checkin_id):
        super().__init__()
        self.setWindowTitle("Chi tiết check-in")
        self.resize(760, 660)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(12)
        outer.addWidget(page_title("Chi tiết check-in", f"Mã lượt quét #{checkin_id}"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        session = SessionLocal()
        try:
            checkin = session.query(Checkin).filter(Checkin.id == checkin_id).first()
            if not checkin:
                layout.addWidget(QLabel("Check-in không tồn tại"))
                return

            related = self._find_related_checkins(session, checkin)
            cards = QHBoxLayout()
            cards.setSpacing(12)
            for item in related:
                cards.addWidget(self._person_card(item))
            cards.addStretch()
            layout.addLayout(cards)

            scanner_name = "N/A"
            if checkin.scanner_user_id:
                scanner = session.query(User).filter(User.id == checkin.scanner_user_id).first()
                scanner_name = scanner.full_name or scanner.username if scanner else "N/A"

            info_panel = QFrame()
            info_panel.setObjectName("panel")
            info_layout = QVBoxLayout(info_panel)
            info_layout.setContentsMargins(16, 16, 16, 16)
            info_layout.addWidget(QLabel(f"Ngày quét: {checkin.scanned_at}"))
            info_layout.addWidget(QLabel(f"Lễ tân: {scanner_name}"))
            info_layout.addWidget(QLabel(f"Nguồn: {checkin.source or 'N/A'}"))
            info_layout.addWidget(QLabel(f"QR: {checkin.qr_payload or 'N/A'}"))
            if len(related) > 1:
                info_layout.addWidget(QLabel("Loại: Buổi tập PT có hội viên + huấn luyện viên"))
            layout.addWidget(info_panel)

            if checkin.photo and os.path.isfile(checkin.photo):
                photo_title = QLabel("Ảnh chụp khi quét")
                photo_title.setObjectName("sectionLabel")
                layout.addWidget(photo_title)
                photo_label = QLabel()
                photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                photo_label.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13;")
                photo_label.setPixmap(
                    QPixmap(checkin.photo).scaled(
                        680,
                        420,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                layout.addWidget(photo_label)
        finally:
            session.close()

    def _find_related_checkins(self, session, checkin):
        related = [checkin]
        query = session.query(Checkin).filter(Checkin.id != checkin.id)
        if checkin.photo:
            query = query.filter(Checkin.photo == checkin.photo)
        elif checkin.scanned_at:
            start = checkin.scanned_at - timedelta(seconds=3)
            end = checkin.scanned_at + timedelta(seconds=3)
            query = query.filter(Checkin.scanned_at >= start, Checkin.scanned_at <= end)
        else:
            return related
        for item in query.order_by(Checkin.id).all():
            if len(related) >= 2:
                break
            if (checkin.member_id and item.trainer_id) or (checkin.trainer_id and item.member_id):
                related.append(item)
        related.sort(key=lambda item: 0 if item.member_id else 1)
        return related

    def _person_card(self, checkin):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        avatar = QLabel("Không có ảnh")
        avatar.setFixedSize(120, 120)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8;")

        title = "Không rõ"
        lines = []
        avatar_path = None
        if checkin.member:
            user = checkin.member.user
            title = f"Hội viên: {user.full_name or user.username}"
            avatar_path = user.avatar
            lines = [
                f"SĐT: {user.phone or 'N/A'}",
                f"Email: {user.email or 'N/A'}",
                f"Trạng thái: {checkin.member.status or 'active'}",
            ]
        elif checkin.trainer:
            user = checkin.trainer.user
            title = f"PT: {user.full_name or user.username}"
            avatar_path = user.avatar
            lines = [
                f"SĐT: {user.phone or 'N/A'}",
                f"Email: {user.email or 'N/A'}",
                f"Bộ môn: {checkin.trainer.specialty or 'Chưa cập nhật'}",
            ]

        if avatar_path and os.path.isfile(avatar_path):
            avatar.setPixmap(
                QPixmap(avatar_path).scaled(
                    120,
                    120,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        layout.addWidget(avatar)

        details = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("sectionLabel")
        details.addWidget(title_label)
        for line in lines:
            details.addWidget(QLabel(line))
        details.addStretch()
        layout.addLayout(details, 1)
        return panel
