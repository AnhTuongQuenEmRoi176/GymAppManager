from datetime import datetime, time

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import or_
from sqlalchemy.orm import aliased

from app.db import get_session
from app.models import Member, Trainer, TrainingSchedule, User
from app.state import get_current_user
from app.ui.schedule_form import ScheduleForm
from app.ui.theme import configure_table, page_title


STATUS_LABELS = {
    "pending": "Chờ xác nhận",
    "upcoming": "Sắp diễn ra",
    "completed": "Hoàn thành",
    "cancelled": "Đã hủy",
    "no_show": "Vắng mặt",
}


class TabSchedules(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(
            page_title(
                "Quản lý lịch tập và lịch dạy",
                "Admin và lễ tân có thể tạo, sửa, hủy và kiểm tra lịch trùng",
            )
        )

        filters = QFrame()
        filters.setObjectName("panel")
        filter_layout = QHBoxLayout(filters)
        filter_layout.setContentsMargins(16, 14, 16, 14)
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm theo PT, hội viên hoặc nội dung")
        self.date_from = QDateEdit()
        self.date_to = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_to.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        today = QDate.currentDate()
        self.date_from.setDate(QDate(today.year(), today.month(), 1))
        self.date_to.setDate(today.addMonths(1).addDays(-1))

        self.status_combo = QComboBox()
        self.status_combo.addItem("Tất cả trạng thái", None)
        for value, label in STATUS_LABELS.items():
            self.status_combo.addItem(label, value)

        self.btn_reload = QPushButton("↻")
        self.btn_reload.setObjectName("iconButton")
        self.btn_reload.setToolTip("Tải lại danh sách")
        self.btn_add = QPushButton("Thêm lịch")
        self.btn_add.setObjectName("primaryButton")

        filter_layout.addWidget(self.search_input, 2)
        filter_layout.addWidget(QLabel("Từ"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("Đến"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addWidget(self.btn_reload)
        filter_layout.addWidget(self.btn_add)
        layout.addWidget(filters)

        actions = QHBoxLayout()
        self.summary_label = QLabel("0 lịch")
        self.summary_label.setObjectName("mutedLabel")
        self.btn_edit = QPushButton("Sửa lịch đã chọn")
        self.btn_edit.setObjectName("warningButton")
        self.btn_cancel_schedule = QPushButton("Hủy lịch đã chọn")
        self.btn_cancel_schedule.setObjectName("dangerButton")
        actions.addWidget(self.summary_label)
        actions.addStretch()
        actions.addWidget(self.btn_edit)
        actions.addWidget(self.btn_cancel_schedule)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Ngày",
                "Thời gian",
                "PT",
                "Hội viên",
                "Nội dung",
                "Địa điểm",
                "Trạng thái",
                "Ghi chú",
            ]
        )
        configure_table(self.table)
        self.table.setColumnHidden(0, True)
        layout.addWidget(self.table, 1)

        self.search_input.textChanged.connect(self.refresh)
        self.date_from.dateChanged.connect(self.refresh)
        self.date_to.dateChanged.connect(self.refresh)
        self.status_combo.currentIndexChanged.connect(self.refresh)
        self.btn_reload.clicked.connect(self.refresh)
        self.btn_add.clicked.connect(self.add_schedule)
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_cancel_schedule.clicked.connect(self.cancel_selected)
        self.table.doubleClicked.connect(self.edit_selected)
        self.refresh()

    def selected_schedule_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def refresh(self):
        start_date = self.date_from.date().toPyDate()
        end_date = self.date_to.date().toPyDate()
        if end_date < start_date:
            return

        start_at = datetime.combine(start_date, time.min)
        end_at = datetime.combine(end_date, time.max)
        search_value = self.search_input.text().strip()
        status_value = self.status_combo.currentData()

        session = get_session()
        try:
            trainer_user = aliased(User)
            member_user = aliased(User)
            query = (
                session.query(TrainingSchedule, trainer_user, member_user)
                .join(Trainer, Trainer.id == TrainingSchedule.trainer_id)
                .join(trainer_user, trainer_user.id == Trainer.user_id)
                .join(Member, Member.id == TrainingSchedule.member_id)
                .join(member_user, member_user.id == Member.user_id)
                .filter(
                    TrainingSchedule.start_at >= start_at,
                    TrainingSchedule.start_at <= end_at,
                )
            )
            if status_value:
                query = query.filter(TrainingSchedule.status == status_value)
            if search_value:
                like = f"%{search_value}%"
                query = query.filter(
                    or_(
                        trainer_user.full_name.ilike(like),
                        trainer_user.phone.ilike(like),
                        member_user.full_name.ilike(like),
                        member_user.phone.ilike(like),
                        TrainingSchedule.title.ilike(like),
                    )
                )

            rows = query.order_by(TrainingSchedule.start_at.asc()).all()
            self.table.setRowCount(len(rows))
            for row_index, (schedule, trainer_account, member_account) in enumerate(rows):
                values = [
                    str(schedule.id),
                    schedule.start_at.strftime("%d/%m/%Y"),
                    f"{schedule.start_at:%H:%M} - {schedule.end_at:%H:%M}",
                    trainer_account.full_name or trainer_account.username,
                    member_account.full_name or member_account.username,
                    schedule.title,
                    schedule.location or "—",
                    STATUS_LABELS.get(schedule.status, schedule.status),
                    schedule.note or "—",
                ]
                for column, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    if column == 0:
                        item.setData(Qt.ItemDataRole.UserRole, schedule.id)
                    self.table.setItem(row_index, column, item)
            self.summary_label.setText(f"{len(rows)} lịch trong khoảng đã chọn")
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải lịch: {exc}")
        finally:
            session.close()

    def add_schedule(self):
        dialog = ScheduleForm(parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh()

    def edit_selected(self, *_):
        schedule_id = self.selected_schedule_id()
        if not schedule_id:
            QMessageBox.information(self, "Chưa chọn", "Hãy chọn một lịch trong bảng.")
            return
        dialog = ScheduleForm(schedule_id=schedule_id, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh()

    def cancel_selected(self):
        schedule_id = self.selected_schedule_id()
        if not schedule_id:
            QMessageBox.information(self, "Chưa chọn", "Hãy chọn một lịch trong bảng.")
            return
        if (
            QMessageBox.question(
                self,
                "Xác nhận hủy",
                "Bạn chắc chắn muốn hủy lịch đã chọn?",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return

        session = get_session()
        try:
            schedule = session.query(TrainingSchedule).filter(
                TrainingSchedule.id == schedule_id
            ).first()
            if not schedule:
                QMessageBox.warning(self, "Không tìm thấy", "Lịch không còn tồn tại.")
                return
            if schedule.status in {"completed", "cancelled", "no_show"}:
                QMessageBox.warning(
                    self,
                    "Không thể hủy",
                    "Lịch đã kết thúc hoặc đã được hủy trước đó.",
                )
                return
            current_user = get_current_user()
            schedule.status = "cancelled"
            schedule.cancelled_by = current_user.id if current_user else None
            schedule.cancelled_at = datetime.now()
            schedule.updated_at = datetime.now()
            session.commit()
            self.refresh()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể hủy lịch: {exc}")
        finally:
            session.close()
