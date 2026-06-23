from datetime import datetime, time

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QDateEdit,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.db import get_session
from app.models import PTSession, Trainer, Transaction
from app.payroll import PT_SESSION_RATE, calculate_trainer_salary
from app.state import get_current_user, is_admin
from app.ui.theme import configure_table, format_money, page_title


class TabPayroll(QWidget):
    def __init__(self):
        super().__init__()
        self.trainer_rows = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(page_title("Tổng hợp lương", "Tính và thanh toán lương PT theo kỳ"))

        filters = QFrame()
        filters.setObjectName("panel")
        row = QHBoxLayout(filters)
        row.setContentsMargins(16, 14, 16, 14)
        row.addWidget(QLabel("Từ"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        row.addWidget(self.date_from)
        row.addWidget(QLabel("Đến"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setDate(QDate.currentDate())
        row.addWidget(self.date_to)
        row.addWidget(QLabel("Hệ số/buổi"))
        self.session_rate = QDoubleSpinBox()
        self.session_rate.setRange(0, 10000000)
        self.session_rate.setDecimals(0)
        self.session_rate.setSingleStep(10000)
        self.session_rate.setValue(PT_SESSION_RATE)
        row.addWidget(self.session_rate)
        self.btn_reload = QPushButton("↻")
        self.btn_reload.setObjectName("iconButton")
        self.btn_reload.setToolTip("Tải lại bảng lương")
        self.btn_pay = QPushButton("Thanh toán lương")
        self.btn_pay.setObjectName("primaryButton")
        row.addWidget(self.btn_reload)
        row.addStretch()
        row.addWidget(self.btn_pay)
        layout.addWidget(filters)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "PT", "Trạng thái", "Lương cứng", "Buổi PT", "Hệ số/buổi", "Tổng lương"])
        configure_table(self.table)
        layout.addWidget(self.table, 1)

        self.btn_reload.clicked.connect(self.refresh)
        self.btn_pay.clicked.connect(self.pay_selected)

        if not is_admin():
            self.btn_pay.setEnabled(False)
            self.btn_reload.setEnabled(False)
            layout.addWidget(QLabel("Chỉ admin được quản lý thanh toán lương."))
        else:
            self.refresh()

    def _date_range(self):
        start = datetime.combine(self.date_from.date().toPyDate(), time.min)
        end = datetime.combine(self.date_to.date().toPyDate(), time.max)
        return start, end

    def refresh(self):
        if not is_admin():
            return
        start, end = self._date_range()
        rate = self.session_rate.value()
        session = get_session()
        try:
            trainers = session.query(Trainer).order_by(Trainer.id.desc()).all()
            self.trainer_rows = []
            self.table.setRowCount(len(trainers))
            for row, trainer in enumerate(trainers):
                session_count = (
                    session.query(PTSession)
                    .filter(PTSession.trainer_id == trainer.id, PTSession.session_date >= start, PTSession.session_date <= end)
                    .count()
                )
                total = calculate_trainer_salary(trainer.base_salary, session_count, rate)
                active = bool(trainer.user and trainer.user.is_active and not trainer.end_date)
                values = [
                    trainer.id,
                    trainer.user.full_name if trainer.user else f"PT {trainer.id}",
                    "Đang làm" if active else "Đã nghỉ",
                    format_money(trainer.base_salary),
                    session_count,
                    format_money(rate),
                    format_money(total),
                ]
                self.trainer_rows.append({"trainer_id": trainer.id, "name": values[1], "sessions": session_count, "rate": rate, "total": total})
                for col, value in enumerate(values):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
        finally:
            session.close()

    def pay_selected(self):
        if not is_admin():
            QMessageBox.warning(self, "Không có quyền", "Chỉ admin được thanh toán lương")
            return
        row = self.table.currentRow()
        if row < 0 or row >= len(self.trainer_rows):
            QMessageBox.information(self, "Chú ý", "Chọn một PT để thanh toán lương")
            return
        item = self.trainer_rows[row]
        if QMessageBox.question(self, "Xác nhận", f"Thanh toán {format_money(item['total'])} cho {item['name']}?") != QMessageBox.StandardButton.Yes:
            return
        current_user = get_current_user()
        start, end = self._date_range()
        session = get_session()
        try:
            tx = Transaction(
                type="salary",
                amount=item["total"],
                date=datetime.now(),
                description=(
                    f"Thanh toán lương PT #{item['trainer_id']} - {item['name']} | "
                    f"Kỳ {start:%d/%m/%Y}-{end:%d/%m/%Y} | "
                    f"{item['sessions']} buổi x {format_money(item['rate'])}"
                ),
                created_by=current_user.id if current_user else None,
            )
            session.add(tx)
            session.commit()
            QMessageBox.information(self, "Thành công", "Đã ghi nhận giao dịch thanh toán lương")
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Thanh toán thất bại: {exc}")
        finally:
            session.close()
        self.refresh()
