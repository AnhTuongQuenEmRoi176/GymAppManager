from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.db import SessionLocal
from app.models import Member, MemberPackage, Package, Trainer, Transaction, User
from app.state import get_current_user
from app.ui.theme import configure_table, format_money, page_title


class PackageRegistrationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng ký gói tập")
        self.resize(760, 560)

        self.session = SessionLocal()
        self.current_user = get_current_user()
        self.selected_package = None
        self.selected_member = None
        self.selected_trainer = None
        self.selected_pt_sessions = 0
        self.pt_fee_by_count = {10: 700000, 30: 600000, 50: 500000, 72: 400000}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(14)
        main_layout.addWidget(page_title("Đăng ký gói tập", "Chọn gói, hội viên, PT và xác nhận thanh toán"))

        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked, 1)
        self.stacked.addWidget(self._create_package_page())
        self.stacked.addWidget(self._create_member_page())
        self.stacked.addWidget(self._create_trainer_page())
        self.stacked.addWidget(self._create_confirm_page())

    def _panel_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        label = QLabel(title)
        label.setObjectName("sectionLabel")
        layout.addWidget(label)
        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.setSpacing(12)
        layout.addWidget(panel, 1)
        return page, panel_layout

    def _create_package_page(self):
        page, layout = self._panel_page("Bước 1: Chọn gói tập")
        self.package_table = QTableWidget()
        self.package_table.setColumnCount(4)
        self.package_table.setHorizontalHeaderLabels(["ID", "Tên gói", "Giá", "Thời hạn"])
        configure_table(self.package_table)

        packages = self.session.query(Package).order_by(Package.price.asc()).all()
        self.package_table.setRowCount(len(packages))
        for row, package in enumerate(packages):
            values = [package.id, package.name, format_money(package.price), f"{package.duration_days} ngày"]
            for col, value in enumerate(values):
                self.package_table.setItem(row, col, QTableWidgetItem(str(value)))
        self.package_table.itemSelectionChanged.connect(self._on_package_selected)
        layout.addWidget(self.package_table, 1)
        layout.addLayout(self._nav_buttons(None, self._next_step))
        return page

    def _create_member_page(self):
        page, layout = self._panel_page("Bước 2: Chọn hội viên")
        self.member_combo = QComboBox()
        members = self.session.query(Member).join(User).order_by(User.full_name).all()
        for member in members:
            self.member_combo.addItem(f"{member.user.full_name} - {member.user.phone or 'N/A'}", member.id)
        layout.addWidget(self.member_combo)
        layout.addStretch()
        layout.addLayout(self._nav_buttons(lambda: self.stacked.setCurrentIndex(0), self._next_step))
        return page

    def _create_trainer_page(self):
        page, layout = self._panel_page("Bước 3: Chọn PT tùy chọn")
        self.trainer_combo = QComboBox()
        self.trainer_combo.addItem("Không chọn PT", None)
        trainers = self.session.query(Trainer).join(User).order_by(User.full_name).all()
        for trainer in trainers:
            self.trainer_combo.addItem(f"{trainer.user.full_name} - {trainer.specialty or 'Chưa cập nhật'}", trainer.id)
        layout.addWidget(self.trainer_combo)

        self.pt_package_combo = QComboBox()
        self.pt_package_combo.addItem("Không chọn số buổi PT", None)
        for count, price_per_session in self.pt_fee_by_count.items():
            self.pt_package_combo.addItem(f"{count} buổi - {format_money(price_per_session)}/buổi", count)
        self.pt_package_combo.setEnabled(False)
        layout.addWidget(self.pt_package_combo)

        self.label_pt_fee = QLabel("Phí PT: 0 VND")
        self.label_pt_fee.setObjectName("sectionLabel")
        layout.addWidget(self.label_pt_fee)
        layout.addStretch()
        layout.addLayout(self._nav_buttons(lambda: self.stacked.setCurrentIndex(1), self._next_step))

        self.trainer_combo.currentIndexChanged.connect(self.on_trainer_changed)
        self.pt_package_combo.currentIndexChanged.connect(self.on_pt_package_changed)
        return page

    def _create_confirm_page(self):
        page, layout = self._panel_page("Bước 4: Xác nhận thanh toán")
        self.label_package_info = QLabel()
        self.label_member_info = QLabel()
        self.label_trainer_info = QLabel()
        self.label_price = QLabel()
        self.label_duration = QLabel()
        self.label_pt_fee_confirm = QLabel()
        self.label_total_payment = QLabel()
        self.label_total_payment.setObjectName("pageTitle")

        for caption, widget in [
            ("Gói tập", self.label_package_info),
            ("Hội viên", self.label_member_info),
            ("PT", self.label_trainer_info),
            ("Giá gói", self.label_price),
            ("Thời hạn", self.label_duration),
            ("Phí PT", self.label_pt_fee_confirm),
        ]:
            label = QLabel(caption)
            label.setObjectName("mutedLabel")
            layout.addWidget(label)
            layout.addWidget(widget)
        layout.addWidget(self.label_total_payment)
        layout.addStretch()

        nav = QHBoxLayout()
        btn_back = QPushButton("Quay lại")
        btn_confirm = QPushButton("Xác nhận thanh toán")
        btn_confirm.setObjectName("primaryButton")
        btn_back.clicked.connect(lambda: self.stacked.setCurrentIndex(2))
        btn_confirm.clicked.connect(self._confirm_registration)
        nav.addWidget(btn_back)
        nav.addStretch()
        nav.addWidget(btn_confirm)
        layout.addLayout(nav)
        return page

    def _nav_buttons(self, back_handler, next_handler):
        nav = QHBoxLayout()
        if back_handler:
            btn_back = QPushButton("Quay lại")
            btn_back.clicked.connect(back_handler)
            nav.addWidget(btn_back)
        nav.addStretch()
        btn_next = QPushButton("Tiếp tục")
        btn_next.setObjectName("primaryButton")
        btn_next.clicked.connect(next_handler)
        nav.addWidget(btn_next)
        return nav

    def _on_package_selected(self):
        row = self.package_table.currentRow()
        if row >= 0 and self.package_table.item(row, 0):
            package_id = int(self.package_table.item(row, 0).text())
            self.selected_package = self.session.query(Package).filter(Package.id == package_id).first()

    def _next_step(self):
        current = self.stacked.currentIndex()
        if current == 0:
            if not self.selected_package:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn gói tập")
                return
            self.stacked.setCurrentIndex(1)
        elif current == 1:
            member_id = self.member_combo.currentData()
            if not member_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn hội viên")
                return
            self.selected_member = self.session.query(Member).filter(Member.id == member_id).first()
            self.stacked.setCurrentIndex(2)
        elif current == 2:
            trainer_id = self.trainer_combo.currentData()
            self.selected_trainer = self.session.query(Trainer).filter(Trainer.id == trainer_id).first() if trainer_id else None
            self.selected_pt_sessions = self.pt_package_combo.currentData() or 0
            self._update_confirm_page()
            self.stacked.setCurrentIndex(3)

    def _calculate_pt_fee(self):
        trainer_selected = bool(self.trainer_combo.currentData())
        pt_count = self.pt_package_combo.currentData() or 0
        if trainer_selected and pt_count in self.pt_fee_by_count:
            return pt_count * self.pt_fee_by_count[pt_count]
        return 0

    def _update_confirm_page(self):
        pt_fee = self._calculate_pt_fee()
        total_payment = float(self.selected_package.price or 0) + pt_fee
        self.label_package_info.setText(f"{self.selected_package.name} ({self.selected_package.sessions or 0} buổi)")
        self.label_price.setText(format_money(self.selected_package.price))
        self.label_duration.setText(f"{self.selected_package.duration_days} ngày")
        self.label_member_info.setText(f"{self.selected_member.user.full_name} - {self.selected_member.user.phone or 'N/A'}")
        self.label_trainer_info.setText(self.selected_trainer.user.full_name if self.selected_trainer else "Không chọn")
        self.label_pt_fee_confirm.setText(format_money(pt_fee))
        self.label_total_payment.setText(f"Tổng thanh toán: {format_money(total_payment)}")

    def on_trainer_changed(self, index):
        enabled = bool(self.trainer_combo.currentData())
        self.pt_package_combo.setEnabled(enabled)
        if not enabled:
            self.pt_package_combo.setCurrentIndex(0)
        self.on_pt_package_changed(self.pt_package_combo.currentIndex())

    def on_pt_package_changed(self, index):
        self.selected_pt_sessions = self.pt_package_combo.currentData() or 0
        self.label_pt_fee.setText(f"Phí PT: {format_money(self._calculate_pt_fee())}")

    def _confirm_registration(self):
        try:
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=self.selected_package.duration_days)
            pt_fee = self._calculate_pt_fee()
            total_payment = float(self.selected_package.price or 0) + pt_fee

            member_package = MemberPackage(
                member_id=self.selected_member.id,
                package_id=self.selected_package.id,
                start_date=start_date,
                end_date=end_date,
                sessions_remaining=self.selected_package.sessions or 0,
                pt_id=self.selected_trainer.id if self.selected_trainer else None,
                price_paid=total_payment,
            )
            self.session.add(member_package)
            self.session.flush()

            transaction = Transaction(
                type="payment",
                amount=total_payment,
                date=datetime.now(),
                description=f"Thanh toán gói {self.selected_package.name} cho {self.selected_member.user.full_name}",
                created_by=self.current_user.id if self.current_user else None,
            )
            self.session.add(transaction)
            self.session.commit()

            QMessageBox.information(self, "Thành công", "Đăng ký gói tập thành công")
            self.accept()
        except Exception as exc:
            self.session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Đăng ký thất bại: {exc}")

    def closeEvent(self, event):
        self.session.close()
        super().closeEvent(event)
