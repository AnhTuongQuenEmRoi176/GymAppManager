from datetime import datetime, time

import matplotlib.pyplot as plt
import pandas as pd
import pyqtgraph as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from pyqtgraph import PlotWidget
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
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
from app.models import MemberPackage, PTSession, Package, Trainer, Transaction
from app.state import is_admin
from app.ui.theme import configure_table, format_money, page_title


class TabReports(QWidget):
    def __init__(self):
        super().__init__()
        self.pt_summary = []
        self.package_summary = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(page_title("Thống kê doanh thu", "Báo cáo doanh thu, lương PT và lãi/lỗ"))

        filters = QFrame()
        filters.setObjectName("panel")
        filters_layout = QHBoxLayout(filters)
        filters_layout.setContentsMargins(16, 14, 16, 14)
        filters_layout.addWidget(QLabel("Từ"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        filters_layout.addWidget(self.date_from)
        filters_layout.addWidget(QLabel("Đến"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filters_layout.addWidget(self.date_to)
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tất cả", "payment", "salary", "refund", "other"])
        filters_layout.addWidget(QLabel("Loại"))
        filters_layout.addWidget(self.type_filter)
        self.btn_view = QPushButton("Xem báo cáo")
        self.btn_view.setObjectName("primaryButton")
        self.btn_export = QPushButton("Xuất Excel")
        filters_layout.addWidget(self.btn_view)
        filters_layout.addWidget(self.btn_export)
        filters_layout.addStretch()
        layout.addWidget(filters)

        summary_layout = QHBoxLayout()
        self.label_revenue = self._stat_card("Doanh thu", "0 VND")
        self.label_salary = self._stat_card("Lương PT", "0 VND")
        self.label_profit = self._stat_card("Lãi/Lỗ", "0 VND")
        summary_layout.addWidget(self.label_revenue["frame"])
        summary_layout.addWidget(self.label_salary["frame"])
        summary_layout.addWidget(self.label_profit["frame"])
        layout.addLayout(summary_layout)

        charts_panel = QFrame()
        charts_panel.setObjectName("panel")
        self.charts_layout = QHBoxLayout(charts_panel)
        self.charts_layout.setContentsMargins(16, 16, 16, 16)
        self.charts_layout.setSpacing(16)
        layout.addWidget(charts_panel, 1)

        self.table = QTableWidget()
        configure_table(self.table)
        layout.addWidget(self.table, 1)

        lower_tables = QHBoxLayout()
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(3)
        self.summary_table.setHorizontalHeaderLabels(["PT", "Số buổi", "Doanh thu ước tính"])
        configure_table(self.summary_table)
        self.package_summary_table = QTableWidget()
        self.package_summary_table.setColumnCount(3)
        self.package_summary_table.setHorizontalHeaderLabels(["Gói", "Lượt đăng ký", "Doanh thu"])
        configure_table(self.package_summary_table)
        lower_tables.addWidget(self.summary_table)
        lower_tables.addWidget(self.package_summary_table)
        layout.addLayout(lower_tables, 1)

        self.btn_view.clicked.connect(self.view_report)
        self.btn_export.clicked.connect(self.export_excel)

        if not is_admin():
            self.btn_view.setEnabled(False)
            self.btn_export.setEnabled(False)
            note = QLabel("Bạn không có quyền xem báo cáo doanh thu.")
            note.setObjectName("mutedLabel")
            layout.addWidget(note)

    def _stat_card(self, caption, value):
        frame = QFrame()
        frame.setObjectName("statCard")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(16, 14, 16, 14)
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        caption_label = QLabel(caption)
        caption_label.setObjectName("statCaption")
        frame_layout.addWidget(value_label)
        frame_layout.addWidget(caption_label)
        return {"frame": frame, "value": value_label}

    def _date_range(self):
        dfrom = self.date_from.date().toPyDate()
        dto = self.date_to.date().toPyDate()
        return datetime.combine(dfrom, time.min), datetime.combine(dto, time.max)

    def _clear_charts(self):
        for i in reversed(range(self.charts_layout.count())):
            item = self.charts_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def view_report(self):
        start_dt, end_dt = self._date_range()
        type_filter = self.type_filter.currentText()

        session = get_session()
        try:
            query = session.query(Transaction).filter(Transaction.date >= start_dt, Transaction.date <= end_dt)
            if type_filter != "Tất cả":
                query = query.filter(Transaction.type == type_filter)
            transactions = query.order_by(Transaction.date.desc()).all()

            rows = []
            total_revenue = 0
            total_salary = 0
            type_sums = {}
            for tx in transactions:
                amount = float(tx.amount or 0)
                rows.append({"date": tx.date, "type": tx.type, "amount": amount, "description": tx.description})
                type_sums[tx.type] = type_sums.get(tx.type, 0) + amount
                if tx.type == "payment":
                    total_revenue += amount
                elif tx.type == "salary":
                    total_salary += amount

            pt_sessions = session.query(PTSession).filter(PTSession.session_date >= start_dt, PTSession.session_date <= end_dt).all()
            trainer_counts = {}
            for pt_session in pt_sessions:
                trainer_counts[pt_session.trainer_id] = trainer_counts.get(pt_session.trainer_id, 0) + 1

            trainer_names = {}
            if trainer_counts:
                trainers = session.query(Trainer).filter(Trainer.id.in_(list(trainer_counts.keys()))).all()
                trainer_names = {trainer.id: trainer.user.full_name or f"PT {trainer.id}" for trainer in trainers}

            trainer_revenue = {}
            for pt_session in pt_sessions:
                if not pt_session.trainer_id:
                    continue
                member_package = (
                    session.query(MemberPackage)
                    .filter(
                        MemberPackage.member_id == pt_session.member_id,
                        MemberPackage.start_date <= pt_session.session_date,
                        MemberPackage.end_date >= pt_session.session_date,
                    )
                    .order_by(MemberPackage.created_at.desc())
                    .first()
                )
                package_price = 0
                if member_package:
                    package_price = float(member_package.price_paid or 0)
                    if not package_price and member_package.package:
                        package_price = float(member_package.package.price or 0)
                trainer_revenue[pt_session.trainer_id] = trainer_revenue.get(pt_session.trainer_id, 0) + package_price * 0.005

            member_packages = (
                session.query(MemberPackage)
                .filter(MemberPackage.created_at >= start_dt, MemberPackage.created_at <= end_dt)
                .all()
            )
            package_totals = {}
            package_counts = {}
            for member_package in member_packages:
                package_name = member_package.package.name if member_package.package else f"Gói {member_package.package_id}"
                package_totals[package_name] = package_totals.get(package_name, 0) + float(member_package.price_paid or 0)
                package_counts[package_name] = package_counts.get(package_name, 0) + 1
        finally:
            session.close()

        profit = total_revenue - total_salary
        self.label_revenue["value"].setText(format_money(total_revenue))
        self.label_salary["value"].setText(format_money(total_salary))
        self.label_profit["value"].setText(format_money(profit))

        self._render_charts(type_sums, trainer_counts, trainer_names, trainer_revenue)
        self._render_transaction_table(rows, total_revenue, total_salary, profit)
        self._render_summary_tables(trainer_counts, trainer_names, trainer_revenue, package_totals, package_counts)

    def _render_charts(self, type_sums, trainer_counts, trainer_names, trainer_revenue):
        self._clear_charts()

        fig1, ax1 = plt.subplots(figsize=(4, 3), facecolor="#101f31")
        ax1.set_facecolor("#101f31")
        if type_sums:
            labels = list(type_sums.keys())
            sizes = [type_sums[key] for key in labels]
            ax1.pie(sizes, labels=labels, autopct="%1.1f%%", textprops={"color": "#e8f2ff"})
        ax1.set_title("Loại giao dịch", color="#e8f2ff")
        canvas1 = FigureCanvas(fig1)
        self.charts_layout.addWidget(canvas1)

        fig2, ax2 = plt.subplots(figsize=(4, 3), facecolor="#101f31")
        ax2.set_facecolor("#101f31")
        if trainer_counts:
            names = [trainer_names.get(tid, str(tid)) for tid in trainer_counts.keys()]
            counts = [trainer_counts[tid] for tid in trainer_counts.keys()]
            ax2.bar(names, counts, color="#ccff00")
            ax2.tick_params(axis="x", colors="#e8f2ff", rotation=35)
            ax2.tick_params(axis="y", colors="#e8f2ff")
        ax2.set_title("Buổi PT", color="#e8f2ff")
        canvas2 = FigureCanvas(fig2)
        self.charts_layout.addWidget(canvas2)

        if trainer_revenue:
            pg_widget = PlotWidget()
            pg_widget.setBackground("#101f31")
            trainer_ids = list(trainer_revenue.keys())
            values = [trainer_revenue[tid] for tid in trainer_ids]
            names = [trainer_names.get(tid, str(tid)) for tid in trainer_ids]
            x_values = list(range(len(values)))
            bar = pg.BarGraphItem(x=x_values, height=values, width=0.55, brush="#ccff00")
            pg_widget.addItem(bar)
            pg_widget.getAxis("bottom").setTicks([list(zip(x_values, names))])
            pg_widget.setTitle("Doanh thu PT")
            self.charts_layout.addWidget(pg_widget)

    def _render_transaction_table(self, rows, total_revenue, total_salary, profit):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ngày", "Loại", "Số tiền", "Mô tả"])
        self.table.setRowCount(len(rows) + 3)
        for row, item in enumerate(rows):
            values = [item["date"], item["type"], format_money(item["amount"]), item["description"] or ""]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
        base = len(rows)
        summary_rows = [
            ("Tổng doanh thu", total_revenue),
            ("Tổng lương PT", total_salary),
            ("Lãi/Lỗ", profit),
        ]
        for offset, (label, value) in enumerate(summary_rows):
            self.table.setItem(base + offset, 1, QTableWidgetItem(label))
            self.table.setItem(base + offset, 2, QTableWidgetItem(format_money(value)))

    def _render_summary_tables(self, trainer_counts, trainer_names, trainer_revenue, package_totals, package_counts):
        trainer_ids = list(trainer_revenue.keys())
        self.summary_table.setRowCount(len(trainer_ids))
        self.pt_summary = []
        for row, trainer_id in enumerate(trainer_ids):
            name = trainer_names.get(trainer_id, str(trainer_id))
            sessions = trainer_counts.get(trainer_id, 0)
            revenue = trainer_revenue.get(trainer_id, 0)
            self.summary_table.setItem(row, 0, QTableWidgetItem(name))
            self.summary_table.setItem(row, 1, QTableWidgetItem(str(sessions)))
            self.summary_table.setItem(row, 2, QTableWidgetItem(format_money(revenue)))
            self.pt_summary.append({"pt": name, "sessions": sessions, "estimated_revenue": revenue})

        package_names = list(package_totals.keys())
        self.package_summary_table.setRowCount(len(package_names))
        self.package_summary = []
        for row, package_name in enumerate(package_names):
            count = package_counts.get(package_name, 0)
            revenue = package_totals.get(package_name, 0)
            self.package_summary_table.setItem(row, 0, QTableWidgetItem(package_name))
            self.package_summary_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.package_summary_table.setItem(row, 2, QTableWidgetItem(format_money(revenue)))
            self.package_summary.append({"package": package_name, "count": count, "revenue": revenue})

    def export_excel(self):
        start_dt, end_dt = self._date_range()
        session = get_session()
        try:
            transactions = session.query(Transaction).filter(Transaction.date >= start_dt, Transaction.date <= end_dt).all()
            rows = [
                {"date": tx.date, "type": tx.type, "amount": float(tx.amount or 0), "description": tx.description}
                for tx in transactions
            ]
            df = pd.DataFrame(rows)
        finally:
            session.close()

        path, _ = QFileDialog.getSaveFileName(self, "Lưu file Excel", "", "Excel Files (*.xlsx)")
        if not path:
            return
        if not path.endswith(".xlsx"):
            path += ".xlsx"
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Transactions", index=False)
            if self.pt_summary:
                pd.DataFrame(self.pt_summary).to_excel(writer, sheet_name="PT Revenue", index=False)
            if self.package_summary:
                pd.DataFrame(self.package_summary).to_excel(writer, sheet_name="Package Summary", index=False)
        QMessageBox.information(self, "Hoàn tất", f"Đã lưu báo cáo vào: {path}")
