from datetime import date, datetime

from PyQt6.QtCore import QDateTime
from PyQt6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)
from sqlalchemy import or_

from app.db import get_session
from app.models import Member, MemberPackage, Trainer, TrainingSchedule, User
from app.state import get_current_user
from app.ui.theme import page_title


STATUS_ITEMS = [
    ("Sắp diễn ra", "upcoming"),
    ("Chờ xác nhận", "pending"),
    ("Hoàn thành", "completed"),
    ("Đã hủy", "cancelled"),
    ("Vắng mặt", "no_show"),
]


class ScheduleForm(QDialog):
    def __init__(self, schedule_id=None, parent=None):
        super().__init__(parent)
        self.schedule_id = schedule_id
        self.setWindowTitle("Lịch tập / lịch dạy")
        self.resize(620, 610)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(
            page_title(
                "Thông tin lịch dạy",
                "Chọn PT, hội viên đang có gói PT và khung giờ không bị trùng",
            )
        )

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(14)

        self.trainer_combo = QComboBox()
        self.member_combo = QComboBox()
        self.title_input = QLineEdit()
        self.start_input = QDateTimeEdit()
        self.end_input = QDateTimeEdit()
        self.location_input = QLineEdit()
        self.status_combo = QComboBox()
        self.note_input = QTextEdit()

        self.start_input.setCalendarPopup(True)
        self.end_input.setCalendarPopup(True)
        self.start_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.end_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.note_input.setPlaceholderText("Mục tiêu hoặc lưu ý cho buổi tập")
        self.note_input.setMaximumHeight(110)
        self.title_input.setPlaceholderText("Ví dụ: Tập ngực - vai")
        self.location_input.setPlaceholderText("Ví dụ: Khu PT tầng 2")

        now = QDateTime.currentDateTime()
        default_start = QDateTime(now.date().addDays(1), now.time())
        default_start = default_start.addSecs(3600)
        self.start_input.setDateTime(default_start)
        self.end_input.setDateTime(default_start.addSecs(3600))

        for label, value in STATUS_ITEMS:
            self.status_combo.addItem(label, value)

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Huấn luyện viên *", self.trainer_combo)
        form.addRow("Hội viên / gói PT *", self.member_combo)
        form.addRow("Nội dung buổi tập *", self.title_input)
        form.addRow("Bắt đầu *", self.start_input)
        form.addRow("Kết thúc *", self.end_input)
        form.addRow("Địa điểm", self.location_input)
        form.addRow("Trạng thái", self.status_combo)
        form.addRow("Ghi chú", self.note_input)
        panel_layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setObjectName("ghostButton")
        self.btn_save = QPushButton("Lưu lịch")
        self.btn_save.setObjectName("primaryButton")
        buttons.addWidget(self.btn_cancel)
        buttons.addWidget(self.btn_save)
        panel_layout.addLayout(buttons)
        layout.addWidget(panel)

        self.trainer_combo.currentIndexChanged.connect(self.reload_members)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self.save)

        self.load_trainers()
        if self.schedule_id:
            self.load_schedule()
        else:
            self.reload_members()

    def load_trainers(self):
        session = get_session()
        try:
            rows = (
                session.query(Trainer)
                .join(Trainer.user)
                .filter(
                    User.is_active.is_(True),
                    or_(Trainer.end_date.is_(None), Trainer.end_date >= date.today()),
                )
                .order_by(User.full_name.asc())
                .all()
            )
            self.trainer_combo.clear()
            for trainer in rows:
                name = trainer.user.full_name or trainer.user.username or f"PT {trainer.id}"
                self.trainer_combo.addItem(name, trainer.id)
        finally:
            session.close()

    def reload_members(self, selected_package_id=None):
        trainer_id = self.trainer_combo.currentData()
        self.member_combo.clear()
        if not trainer_id:
            return

        session = get_session()
        try:
            rows = (
                session.query(MemberPackage, Member, User)
                .join(Member, Member.id == MemberPackage.member_id)
                .join(User, User.id == Member.user_id)
                .filter(
                    MemberPackage.pt_id == trainer_id,
                    MemberPackage.end_date >= date.today(),
                    User.is_active.is_(True),
                    or_(
                        MemberPackage.sessions_remaining.is_(None),
                        MemberPackage.sessions_remaining > 0,
                    ),
                )
                .order_by(User.full_name.asc(), MemberPackage.end_date.desc())
                .all()
            )
            for member_package, member, user in rows:
                remaining = (
                    "không giới hạn"
                    if member_package.sessions_remaining is None
                    else f"còn {member_package.sessions_remaining} buổi"
                )
                label = f"{user.full_name or user.username} • {remaining} • hết hạn {member_package.end_date:%d/%m/%Y}"
                self.member_combo.addItem(
                    label,
                    {
                        "member_id": member.id,
                        "member_package_id": member_package.id,
                    },
                )
                if selected_package_id == member_package.id:
                    self.member_combo.setCurrentIndex(self.member_combo.count() - 1)
        finally:
            session.close()

    def load_schedule(self):
        session = get_session()
        try:
            schedule = session.query(TrainingSchedule).filter(
                TrainingSchedule.id == self.schedule_id
            ).first()
            if not schedule:
                QMessageBox.warning(self, "Không tìm thấy", "Lịch không còn tồn tại.")
                self.reject()
                return

            trainer_index = self.trainer_combo.findData(schedule.trainer_id)
            if trainer_index >= 0:
                self.trainer_combo.setCurrentIndex(trainer_index)
            self.reload_members(schedule.member_package_id)

            self.title_input.setText(schedule.title or "")
            self.location_input.setText(schedule.location or "")
            self.note_input.setPlainText(schedule.note or "")
            self.start_input.setDateTime(QDateTime(schedule.start_at))
            self.end_input.setDateTime(QDateTime(schedule.end_at))
            status_index = self.status_combo.findData(schedule.status)
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)
        finally:
            session.close()

    def save(self):
        trainer_id = self.trainer_combo.currentData()
        member_data = self.member_combo.currentData()
        title = self.title_input.text().strip()
        start_at = self.start_input.dateTime().toPyDateTime()
        end_at = self.end_input.dateTime().toPyDateTime()

        if not trainer_id:
            QMessageBox.warning(self, "Thiếu thông tin", "Hãy chọn huấn luyện viên.")
            return
        if not isinstance(member_data, dict):
            QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "PT chưa có hội viên đang sử dụng gói PT hoặc bạn chưa chọn hội viên.",
            )
            return
        if len(title) < 2:
            QMessageBox.warning(self, "Thiếu thông tin", "Hãy nhập nội dung buổi tập.")
            return
        if end_at <= start_at:
            QMessageBox.warning(
                self,
                "Sai thời gian",
                "Thời gian kết thúc phải sau thời gian bắt đầu.",
            )
            return
        if start_at < datetime.now() and not self.schedule_id:
            QMessageBox.warning(self, "Sai thời gian", "Không thể tạo lịch ở thời điểm đã qua.")
            return

        member_id = member_data["member_id"]
        member_package_id = member_data["member_package_id"]
        session = get_session()
        try:
            conflict_query = session.query(TrainingSchedule).filter(
                TrainingSchedule.status.in_(["pending", "upcoming"]),
                TrainingSchedule.start_at < end_at,
                TrainingSchedule.end_at > start_at,
                or_(
                    TrainingSchedule.trainer_id == trainer_id,
                    TrainingSchedule.member_id == member_id,
                ),
            )
            if self.schedule_id:
                conflict_query = conflict_query.filter(
                    TrainingSchedule.id != self.schedule_id
                )
            if conflict_query.first():
                QMessageBox.warning(
                    self,
                    "Trùng lịch",
                    "PT hoặc hội viên đã có lịch trong khung giờ này.",
                )
                return

            if self.schedule_id:
                schedule = session.query(TrainingSchedule).filter(
                    TrainingSchedule.id == self.schedule_id
                ).first()
                if not schedule:
                    QMessageBox.warning(self, "Không tìm thấy", "Lịch không còn tồn tại.")
                    return
            else:
                current_user = get_current_user()
                schedule = TrainingSchedule(
                    created_by=current_user.id if current_user else None,
                    created_at=datetime.now(),
                )
                session.add(schedule)

            schedule.trainer_id = trainer_id
            schedule.member_id = member_id
            schedule.member_package_id = member_package_id
            schedule.title = title
            schedule.start_at = start_at
            schedule.end_at = end_at
            schedule.location = self.location_input.text().strip() or None
            schedule.note = self.note_input.toPlainText().strip() or None
            schedule.status = self.status_combo.currentData() or "upcoming"
            schedule.updated_at = datetime.now()

            if schedule.status == "cancelled":
                current_user = get_current_user()
                schedule.cancelled_by = current_user.id if current_user else None
                schedule.cancelled_at = datetime.now()
            else:
                schedule.cancelled_by = None
                schedule.cancelled_at = None

            session.commit()
            self.accept()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu lịch: {exc}")
        finally:
            session.close()
