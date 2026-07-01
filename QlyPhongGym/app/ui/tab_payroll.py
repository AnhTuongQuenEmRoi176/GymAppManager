from datetime import datetime, time

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
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

from app.db import get_session
from app.models import PTSession, Role, Trainer, Transaction, User
from app.payroll import DEFAULT_RECEPTIONIST_SALARY, PT_SESSION_RATE, calculate_trainer_salary, salary_token
from app.state import get_current_user, is_admin
from app.ui.theme import configure_table, format_money, page_title


class TabPayroll(QWidget):
    def __init__(self):
        super().__init__()
        self.employee_rows = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(page_title("Tổng hợp lương", "Lương PT, lễ tân, thanh toán và xuất Excel"))

        filters = QFrame()
        filters.setObjectName("panel")
        row = QHBoxLayout(filters)
        row.setContentsMargins(16, 14, 16, 14)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Tìm theo tên, SĐT, vai trò")
        row.addWidget(self.search, 1)
        row.addWidget(QLabel("Từ"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        today = QDate.currentDate()
        self.date_from.setDate(QDate(today.year(), today.month(), 1))
        row.addWidget(self.date_from)
        row.addWidget(QLabel("Đến"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setDate(today)
        row.addWidget(self.date_to)
        self.btn_month = QPushButton("Tháng này")
        self.btn_month.setObjectName("ghostButton")
        row.addWidget(self.btn_month)
        layout.addWidget(filters)

        controls = QFrame()
        controls.setObjectName("panel")
        control_row = QHBoxLayout(controls)
        control_row.setContentsMargins(16, 14, 16, 14)
        control_row.addWidget(QLabel("Hệ số/buổi PT"))
        self.session_rate = QDoubleSpinBox()
        self.session_rate.setRange(0, 10000000)
        self.session_rate.setDecimals(0)
        self.session_rate.setSingleStep(10000)
        self.session_rate.setValue(PT_SESSION_RATE)
        control_row.addWidget(self.session_rate)
        control_row.addWidget(QLabel("Lương lễ tân/kỳ"))
        self.receptionist_salary = QDoubleSpinBox()
        self.receptionist_salary.setRange(0, 100000000)
        self.receptionist_salary.setDecimals(0)
        self.receptionist_salary.setSingleStep(500000)
        self.receptionist_salary.setValue(DEFAULT_RECEPTIONIST_SALARY)
        control_row.addWidget(self.receptionist_salary)
        control_row.addWidget(QLabel("Sắp xếp"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Tên A-Z", "Tổng lương cao", "Còn phải trả cao", "Số buổi PT cao", "Vai trò"])
        control_row.addWidget(self.sort_combo)
        self.btn_reload = QPushButton("↻")
        self.btn_reload.setObjectName("iconButton")
        self.btn_reload.setToolTip("Tải lại bảng lương")
        self.btn_export = QPushButton("Xuất Excel")
        self.btn_export.setObjectName("secondaryButton")
        self.btn_pay = QPushButton("Thanh toán lương")
        self.btn_pay.setObjectName("primaryButton")
        control_row.addWidget(self.btn_reload)
        control_row.addStretch()
        control_row.addWidget(self.btn_export)
        control_row.addWidget(self.btn_pay)
        layout.addWidget(controls)

        summary = QHBoxLayout()
        self.total_payroll = self._metric("Tổng lương", "0 VND")
        self.total_paid = self._metric("Đã thanh toán", "0 VND")
        self.total_due = self._metric("Còn phải trả", "0 VND")
        summary.addWidget(self.total_payroll["frame"])
        summary.addWidget(self.total_paid["frame"])
        summary.addWidget(self.total_due["frame"])
        layout.addLayout(summary)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["ID", "Loại", "Nhân viên", "SĐT", "Trạng thái", "Lương cứng", "Buổi PT", "Tổng lương", "Đã trả", "Còn phải trả"])
        configure_table(self.table)
        layout.addWidget(self.table, 1)

        self.btn_month.clicked.connect(self.set_current_month)
        self.btn_reload.clicked.connect(self.refresh)
        self.btn_pay.clicked.connect(self.pay_selected)
        self.btn_export.clicked.connect(self.export_excel)
        self.search.returnPressed.connect(self.refresh)
        self.sort_combo.currentIndexChanged.connect(self.refresh)
        self.session_rate.valueChanged.connect(self.refresh)
        self.receptionist_salary.valueChanged.connect(self.refresh)

        if not is_admin():
            for widget in (self.search, self.date_from, self.date_to, self.btn_month, self.session_rate, self.receptionist_salary, self.sort_combo, self.btn_reload, self.btn_export, self.btn_pay):
                widget.setEnabled(False)
            layout.addWidget(QLabel("Chỉ admin được quản lý thanh toán lương."))
        else:
            self.refresh()

    def _metric(self, caption, value):
        frame = QFrame()
        frame.setObjectName("statCard")
        metric_layout = QVBoxLayout(frame)
        metric_layout.setContentsMargins(16, 14, 16, 14)
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        caption_label = QLabel(caption)
        caption_label.setObjectName("statCaption")
        metric_layout.addWidget(value_label)
        metric_layout.addWidget(caption_label)
        return {"frame": frame, "value": value_label}

    def set_current_month(self):
        today = QDate.currentDate()
        self.date_from.setDate(QDate(today.year(), today.month(), 1))
        self.date_to.setDate(today)
        self.refresh()

    def _date_range(self):
        start = datetime.combine(self.date_from.date().toPyDate(), time.min)
        end = datetime.combine(self.date_to.date().toPyDate(), time.max)
        return start, end

    def _paid_amount(self, session, employee_type, employee_id, start, end):
        token = salary_token(employee_type, employee_id)
        rows = (
            session.query(Transaction)
            .filter(Transaction.type == "salary", Transaction.date >= start, Transaction.date <= end, Transaction.description.ilike(f"%{token}%"))
            .all()
        )
        return sum(float(row.amount or 0) for row in rows)

    def _build_rows(self, session, start, end):
        rate = self.session_rate.value()
        receptionist_base = self.receptionist_salary.value()
        rows = []
        for trainer in session.query(Trainer).join(User).all():
            session_count = (
                session.query(PTSession)
                .filter(PTSession.trainer_id == trainer.id, PTSession.session_date >= start, PTSession.session_date <= end)
                .count()
            )
            total = calculate_trainer_salary(trainer.base_salary, session_count, rate)
            paid = self._paid_amount(session, "trainer", trainer.id, start, end)
            active = bool(trainer.user and trainer.user.is_active and not trainer.end_date)
            rows.append({
                "id": trainer.id,
                "type": "trainer",
                "type_label": "PT",
                "name": trainer.user.full_name or trainer.user.username or f"PT {trainer.id}",
                "phone": trainer.user.phone or "",
                "status": "Đang làm" if active else "Đã nghỉ",
                "base": float(trainer.base_salary or 0),
                "sessions": session_count,
                "total": total,
                "paid": paid,
                "due": max(total - paid, 0),
            })

        role = session.query(Role).filter(Role.name == "receptionist").first()
        if role:
            for user in session.query(User).filter(User.role_id == role.id).all():
                paid = self._paid_amount(session, "receptionist", user.id, start, end)
                rows.append({
                    "id": user.id,
                    "type": "receptionist",
                    "type_label": "Lễ tân",
                    "name": user.full_name or user.username,
                    "phone": user.phone or "",
                    "status": "Đang làm" if user.is_active else "Đã nghỉ",
                    "base": receptionist_base,
                    "sessions": 0,
                    "total": receptionist_base,
                    "paid": paid,
                    "due": max(receptionist_base - paid, 0),
                })
        return rows

    def _apply_filters(self, rows):
        term = self.search.text().strip().lower()
        if term:
            rows = [row for row in rows if term in row["name"].lower() or term in row["phone"].lower() or term in row["type_label"].lower()]
        sort_key = self.sort_combo.currentText()
        if sort_key == "Tổng lương cao":
            rows.sort(key=lambda row: row["total"], reverse=True)
        elif sort_key == "Còn phải trả cao":
            rows.sort(key=lambda row: row["due"], reverse=True)
        elif sort_key == "Số buổi PT cao":
            rows.sort(key=lambda row: row["sessions"], reverse=True)
        elif sort_key == "Vai trò":
            rows.sort(key=lambda row: (row["type_label"], row["name"]))
        else:
            rows.sort(key=lambda row: row["name"])
        return rows

    def refresh(self):
        if not is_admin():
            return
        start, end = self._date_range()
        session = get_session()
        try:
            rows = self._apply_filters(self._build_rows(session, start, end))
            self.employee_rows = rows
            self.table.setRowCount(len(rows))
            for row_index, item in enumerate(rows):
                values = [
                    item["id"], item["type_label"], item["name"], item["phone"], item["status"],
                    format_money(item["base"]), item["sessions"], format_money(item["total"]), format_money(item["paid"]), format_money(item["due"]),
                ]
                for col, value in enumerate(values):
                    self.table.setItem(row_index, col, QTableWidgetItem(str(value)))
            self.total_payroll["value"].setText(format_money(sum(row["total"] for row in rows)))
            self.total_paid["value"].setText(format_money(sum(row["paid"] for row in rows)))
            self.total_due["value"].setText(format_money(sum(row["due"] for row in rows)))
        finally:
            session.close()

    def pay_selected(self):
        if not is_admin():
            QMessageBox.warning(self, "Không có quyền", "Chỉ admin được thanh toán lương")
            return
        row = self.table.currentRow()
        if row < 0 or row >= len(self.employee_rows):
            QMessageBox.information(self, "Chú ý", "Chọn một nhân viên để thanh toán lương")
            return
        item = self.employee_rows[row]
        amount = item["due"]
        if amount <= 0:
            QMessageBox.information(self, "Chú ý", "Nhân viên này không còn lương phải trả trong kỳ")
            return
        if QMessageBox.question(self, "Xác nhận", f"Thanh toán {format_money(amount)} cho {item['name']}?") != QMessageBox.StandardButton.Yes:
            return
        current_user = get_current_user()
        start, end = self._date_range()
        session = get_session()
        try:
            tx = Transaction(
                type="salary", amount=amount, date=datetime.now(),
                description=(
                    f"{salary_token(item['type'], item['id'])} | Thanh toán lương {item['type_label']} - {item['name']} | "
                    f"Kỳ {start:%d/%m/%Y}-{end:%d/%m/%Y} | Buổi PT: {item['sessions']}"
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

    def export_excel(self):
        if not self.employee_rows:
            QMessageBox.information(self, "Chú ý", "Không có dữ liệu để xuất")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Lưu bảng lương", "", "Excel Files (*.xlsx)")
        if not path:
            return
        if not path.endswith(".xlsx"):
            path += ".xlsx"
        import pandas as pd

        start, end = self._date_range()
        rows = []
        for item in self.employee_rows:
            rows.append({
                "period_start": start.date(), "period_end": end.date(), "id": item["id"], "type": item["type_label"],
                "name": item["name"], "phone": item["phone"], "status": item["status"], "base_salary": item["base"],
                "pt_sessions": item["sessions"], "total_salary": item["total"], "paid": item["paid"], "due": item["due"],
            })
        pd.DataFrame(rows).to_excel(path, index=False)
        QMessageBox.information(self, "Thành công", "Đã xuất bảng lương")
