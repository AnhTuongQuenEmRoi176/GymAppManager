import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout

from app.db import get_session
from app.models import Checkin, Member, MemberPackage, PTSession, Trainer, User
from app.ui.theme import configure_table, page_title


class MemberDetailDialog(QDialog):
    def __init__(self, member_id):
        super().__init__()
        self.setWindowTitle("Chi tiết hội viên")
        self.resize(820, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        session = get_session()
        try:
            member = session.query(Member).filter(Member.id == member_id).first()
            if not member:
                layout.addWidget(QLabel("Hội viên không tồn tại"))
                return

            layout.addWidget(page_title("Chi tiết hội viên", member.user.full_name or member.user.username or f"Hội viên {member.id}"))

            panel = QFrame()
            panel.setObjectName("panel")
            top = QHBoxLayout(panel)
            top.setContentsMargins(16, 16, 16, 16)
            top.setSpacing(16)

            avatar = QLabel("Không có ảnh")
            avatar.setFixedSize(120, 120)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8;")
            if member.user.avatar and os.path.isfile(member.user.avatar):
                avatar.setPixmap(QPixmap(member.user.avatar).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            top.addWidget(avatar)

            info = QLabel(
                f"Tên: {member.user.full_name or ''}\n"
                f"SĐT: {member.user.phone or 'N/A'}\n"
                f"Ngày vào: {member.joined_at.date() if member.joined_at else ''}\n"
                f"Trạng thái: {member.status or 'active'}"
            )
            info.setWordWrap(True)
            top.addWidget(info, 1)
            layout.addWidget(panel)

            layout.addWidget(self._section("Lịch sử check-in"))
            checkin_table = QTableWidget()
            checkin_table.setColumnCount(3)
            checkin_table.setHorizontalHeaderLabels(["Thời gian", "Nguồn", "Ảnh"])
            configure_table(checkin_table)
            records = session.query(Checkin).filter(Checkin.member_id == member.id).order_by(Checkin.scanned_at.desc()).all()
            checkin_table.setRowCount(len(records))
            for row, record in enumerate(records):
                values = [record.scanned_at, record.source or "", record.photo or ""]
                for col, value in enumerate(values):
                    checkin_table.setItem(row, col, QTableWidgetItem(str(value)))
            layout.addWidget(checkin_table)

            layout.addWidget(self._section("Lịch sử gói tập"))
            package_table = QTableWidget()
            package_table.setColumnCount(4)
            package_table.setHorizontalHeaderLabels(["Gói", "Bắt đầu", "Kết thúc", "Buổi còn lại"])
            configure_table(package_table)
            member_packages = session.query(MemberPackage).filter(MemberPackage.member_id == member.id).order_by(MemberPackage.created_at.desc()).all()
            package_table.setRowCount(len(member_packages))
            for row, member_package in enumerate(member_packages):
                values = [
                    member_package.package.name if member_package.package else member_package.package_id,
                    member_package.start_date,
                    member_package.end_date,
                    member_package.sessions_remaining if member_package.sessions_remaining is not None else "",
                ]
                for col, value in enumerate(values):
                    package_table.setItem(row, col, QTableWidgetItem(str(value)))
            layout.addWidget(package_table)

            layout.addWidget(self._section("Buổi PT đã xác nhận"))
            pt_table = QTableWidget()
            pt_table.setColumnCount(3)
            pt_table.setHorizontalHeaderLabels(["Ngày", "PT", "Xác nhận bởi"])
            configure_table(pt_table)
            pt_sessions = session.query(PTSession).filter(PTSession.member_id == member.id).order_by(PTSession.session_date.desc()).all()
            pt_table.setRowCount(len(pt_sessions))
            for row, pt_session in enumerate(pt_sessions):
                trainer_name = ""
                confirmer_name = ""
                if pt_session.trainer_id:
                    trainer = session.query(Trainer).filter(Trainer.id == pt_session.trainer_id).first()
                    trainer_name = trainer.user.full_name if trainer and trainer.user else str(pt_session.trainer_id)
                if pt_session.confirmed_by:
                    user = session.query(User).filter(User.id == pt_session.confirmed_by).first()
                    confirmer_name = user.full_name if user else str(pt_session.confirmed_by)
                values = [pt_session.session_date, trainer_name, confirmer_name]
                for col, value in enumerate(values):
                    pt_table.setItem(row, col, QTableWidgetItem(str(value)))
            layout.addWidget(pt_table)
        finally:
            session.close()

    def _section(self, text):
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        return label
