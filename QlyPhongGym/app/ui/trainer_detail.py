import os
from datetime import date, datetime, time

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout

from app.db import get_session
from app.models import Member, MemberPackage, PTSession, Trainer, User
from app.payroll import PT_SESSION_RATE, calculate_trainer_salary
from app.ui.theme import configure_table, format_money, page_title


class TrainerDetailDialog(QDialog):
    def __init__(self, trainer_id):
        super().__init__()
        self.setWindowTitle("Chi tiết PT")
        self.resize(980, 680)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        today = date.today()
        month_start = datetime.combine(today.replace(day=1), time.min)
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        month_end = datetime.combine(next_month, time.min)

        session = get_session()
        try:
            trainer = session.query(Trainer).filter(Trainer.id == trainer_id).first()
            if not trainer:
                layout.addWidget(QLabel("PT không tồn tại"))
                return

            title = trainer.user.full_name or trainer.user.username or f"PT {trainer.id}"
            layout.addWidget(page_title("Chi tiết PT", f"{title} - thu nhập tháng {today:%m/%Y}"))

            active_packages = session.query(MemberPackage).filter(MemberPackage.pt_id == trainer.id, MemberPackage.end_date >= today).count()
            total_sessions = session.query(PTSession).filter(PTSession.trainer_id == trainer.id).count()
            month_sessions = (
                session.query(PTSession)
                .filter(PTSession.trainer_id == trainer.id, PTSession.session_date >= month_start, PTSession.session_date < month_end)
                .order_by(PTSession.session_date.desc())
                .all()
            )
            month_session_count = len(month_sessions)
            session_income = month_session_count * PT_SESSION_RATE
            month_income = calculate_trainer_salary(trainer.base_salary, month_session_count)

            summary = QHBoxLayout()
            summary.addWidget(self._metric("Buổi tháng này", month_session_count))
            summary.addWidget(self._metric("Hệ số/buổi", format_money(PT_SESSION_RATE)))
            summary.addWidget(self._metric("Tiền theo buổi", format_money(session_income)))
            summary.addWidget(self._metric("Lương cứng", format_money(trainer.base_salary)))
            summary.addWidget(self._metric("Thu nhập tháng", format_money(month_income)))
            layout.addLayout(summary)

            panel = QFrame()
            panel.setObjectName("panel")
            top = QHBoxLayout(panel)
            top.setContentsMargins(16, 16, 16, 16)
            top.setSpacing(16)

            avatar = QLabel("Không có ảnh")
            avatar.setFixedSize(120, 120)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8;")
            if trainer.user.avatar and os.path.isfile(trainer.user.avatar):
                avatar.setPixmap(QPixmap(trainer.user.avatar).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            top.addWidget(avatar)

            status = "Đang làm" if trainer.user and trainer.user.is_active and not trainer.end_date else "Đã nghỉ"
            info = QLabel(
                f"Tên: {trainer.user.full_name or ''}\n"
                f"SĐT: {trainer.user.phone or 'N/A'}\n"
                f"Bộ môn: {trainer.specialty or 'Chưa cập nhật'}\n"
                f"Trạng thái: {status}\n"
                f"Ngày vào: {trainer.start_date or 'Chưa rõ'}\n"
                f"Ngày nghỉ: {trainer.end_date or 'Chưa nghỉ'}\n"
                f"Tổng buổi đã dạy: {total_sessions} | Gói PT hiện tại: {active_packages}"
            )
            top.addWidget(info, 1)
            layout.addWidget(panel)

            title_label = QLabel("Buổi PT trong tháng này")
            title_label.setObjectName("sectionLabel")
            layout.addWidget(title_label)

            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Ngày", "Hội viên", "Xác nhận bởi", "Tiền buổi"])
            configure_table(table)
            table.setRowCount(len(month_sessions))
            for row, pt_session in enumerate(month_sessions):
                member_name = ""
                confirmed_name = ""
                if pt_session.member_id:
                    member = session.query(Member).filter(Member.id == pt_session.member_id).first()
                    member_name = member.user.full_name if member and member.user else str(pt_session.member_id)
                if pt_session.confirmed_by:
                    user = session.query(User).filter(User.id == pt_session.confirmed_by).first()
                    confirmed_name = user.full_name if user else str(pt_session.confirmed_by)
                values = [pt_session.session_date, member_name, confirmed_name, format_money(PT_SESSION_RATE)]
                for col, value in enumerate(values):
                    table.setItem(row, col, QTableWidgetItem(str(value)))
            layout.addWidget(table, 1)
        finally:
            session.close()

    def _metric(self, caption, value):
        frame = QFrame()
        frame.setObjectName("statCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 12, 14, 12)
        value_label = QLabel(str(value))
        value_label.setObjectName("statValue")
        caption_label = QLabel(caption)
        caption_label.setObjectName("statCaption")
        layout.addWidget(value_label)
        layout.addWidget(caption_label)
        return frame
