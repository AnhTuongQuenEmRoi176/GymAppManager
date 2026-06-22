from datetime import timedelta

from PyQt6.QtCore import QDate, QTimer
from PyQt6.QtWidgets import (
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.db import SessionLocal
from app.models import Checkin, User
from app.ui.theme import configure_table, page_title


class TabHistory(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(page_title("Lịch sử check-in", "Tra cứu lượt quét của hội viên và PT theo ngày"))

        filter_panel = QFrame()
        filter_panel.setObjectName("panel")
        filter_layout = QHBoxLayout(filter_panel)
        filter_layout.setContentsMargins(16, 14, 16, 14)
        filter_layout.addWidget(QLabel("Từ ngày"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("Đến ngày"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_to)
        self.btn_filter = QPushButton("Lọc")
        self.btn_filter.setObjectName("primaryButton")
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addStretch()
        layout.addWidget(filter_panel)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Khách/PT", "Ngày giờ", "Loại", "Lễ tân", "Nguồn"])
        configure_table(self.table)
        layout.addWidget(self.table, 1)

        self.btn_filter.clicked.connect(self.load_checkins)
        self.table.itemDoubleClicked.connect(self.open_detail)

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_checkins)
        self.refresh_timer.start(10000)
        self.load_checkins()

    def __del__(self):
        if hasattr(self, "refresh_timer"):
            self.refresh_timer.stop()

    def load_checkins(self):
        dfrom = self.date_from.date().toPyDate()
        dto = self.date_to.date().toPyDate() + timedelta(days=1)

        session = SessionLocal()
        try:
            checkins = (
                session.query(Checkin)
                .filter(Checkin.scanned_at >= dfrom, Checkin.scanned_at < dto)
                .order_by(Checkin.scanned_at.desc())
                .all()
            )
            self.table.setRowCount(len(checkins))
            for row, checkin in enumerate(checkins):
                name = ""
                if checkin.member:
                    name = checkin.member.user.full_name or checkin.member.user.username
                elif checkin.trainer:
                    name = checkin.trainer.user.full_name or checkin.trainer.user.username
                checkin_type = "Hội viên" if checkin.member else ("PT" if checkin.trainer else "")
                receptionist_name = "N/A"
                if checkin.scanner_user_id:
                    user = session.query(User).filter(User.id == checkin.scanner_user_id).first()
                    receptionist_name = user.full_name if user else "N/A"
                values = [
                    checkin.id,
                    name,
                    checkin.scanned_at or "",
                    checkin_type,
                    receptionist_name,
                    checkin.source or checkin.qr_payload or "",
                ]
                for col, value in enumerate(values):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
        finally:
            session.close()

    def open_detail(self, item):
        row = self.table.currentRow()
        if row < 0 or not self.table.item(row, 0):
            return
        checkin_id = int(self.table.item(row, 0).text())
        from app.ui.checkin_detail import CheckinDetailDialog

        dlg = CheckinDetailDialog(checkin_id)
        dlg.exec()
