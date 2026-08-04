from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

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
from app.models import (
    Member,
    MemberPackage,
    Package,
    Payment,
    Trainer,
    Transaction,
    User,
)
from app.state import get_current_user
from app.ui.theme import configure_table, format_money, page_title


class PackageRegistrationDialog(QDialog):
    """Register a base package and an optional PT add-on consistently.

    A GYM package and a PT add-on are stored as two member_packages rows. This
    avoids overwriting a 26-entry GYM counter with a 10/30/50/72-session PT
    counter. PT and COMBO packages are stored as one row and require a trainer.
    """

    PT_UNIT_PRICE = {
        10: Decimal("700000"),
        30: Decimal("600000"),
        50: Decimal("500000"),
        72: Decimal("400000"),
    }
    PT_DURATION_DAYS = {10: 60, 30: 180, 50: 300, 72: 365}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng ký gói tập")
        self.resize(860, 640)

        self.session = SessionLocal()
        self.current_user = get_current_user()
        self.selected_package = None
        self.selected_member = None
        self.selected_trainer = None
        self.selected_pt_sessions = 0

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(14)
        main_layout.addWidget(
            page_title(
                "Đăng ký gói tập",
                "Dữ liệu đăng ký được đồng bộ",
            )
        )

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
        page, layout = self._panel_page("Bước 1: Chọn gói tập chính")
        self.package_table = QTableWidget()
        self.package_table.setColumnCount(6)
        self.package_table.setHorizontalHeaderLabels(
            ["ID", "Tên gói", "Loại", "Giá", "Thời hạn", "Số lượt/buổi"]
        )
        configure_table(self.package_table)

        packages = (
            self.session.query(Package)
            .filter(Package.is_active == True)  # noqa: E712
            .order_by(Package.price.asc(), Package.id.asc())
            .all()
        )
        self.package_table.setRowCount(len(packages))
        for row, package in enumerate(packages):
            values = [
                package.id,
                package.name,
                (package.package_type or "GYM").upper(),
                format_money(package.price),
                f"{package.duration_days} ngày",
                package.sessions if package.sessions is not None else "Không giới hạn",
            ]
            for col, value in enumerate(values):
                self.package_table.setItem(row, col, QTableWidgetItem(str(value)))

        self.package_table.itemSelectionChanged.connect(self._on_package_selected)
        layout.addWidget(self.package_table, 1)
        layout.addLayout(self._nav_buttons(None, self._next_step))
        return page

    def _create_member_page(self):
        page, layout = self._panel_page("Bước 2: Chọn hội viên")
        self.member_combo = QComboBox()
        members = (
            self.session.query(Member)
            .join(User)
            .filter(User.is_active == True)  # noqa: E712
            .order_by(User.full_name.asc(), Member.id.asc())
            .all()
        )
        for member in members:
            self.member_combo.addItem(
                f"{member.user.full_name or member.user.username} - "
                f"{member.user.phone or 'N/A'}",
                member.id,
            )
        layout.addWidget(self.member_combo)
        layout.addStretch()
        layout.addLayout(
            self._nav_buttons(lambda: self.stacked.setCurrentIndex(0), self._next_step)
        )
        return page

    def _create_trainer_page(self):
        page, layout = self._panel_page("Bước 3: Chọn PT")

        self.trainer_hint = QLabel(
            "Gói GYM có thể mua thêm gói PT. Gói PT/COMBO bắt buộc chọn PT."
        )
        self.trainer_hint.setWordWrap(True)
        self.trainer_hint.setObjectName("mutedLabel")
        layout.addWidget(self.trainer_hint)

        self.trainer_combo = QComboBox()
        self.trainer_combo.addItem("Không chọn PT", None)
        trainers = (
            self.session.query(Trainer)
            .join(User)
            .filter(User.is_active == True, Trainer.end_date == None)  # noqa: E711,E712
            .order_by(User.full_name.asc())
            .all()
        )
        for trainer in trainers:
            self.trainer_combo.addItem(
                f"{trainer.user.full_name or trainer.user.username} - "
                f"{trainer.specialty or 'Chưa cập nhật'}",
                trainer.id,
            )
        layout.addWidget(self.trainer_combo)

        self.pt_package_combo = QComboBox()
        self.pt_package_combo.addItem("Không mua thêm gói PT", None)
        for count, unit_price in self.PT_UNIT_PRICE.items():
            self.pt_package_combo.addItem(
                f"{count} buổi - {format_money(unit_price)}/buổi",
                count,
            )
        self.pt_package_combo.setEnabled(False)
        layout.addWidget(self.pt_package_combo)

        self.label_pt_fee = QLabel("Phí PT: 0 VND")
        self.label_pt_fee.setObjectName("sectionLabel")
        layout.addWidget(self.label_pt_fee)
        layout.addStretch()
        layout.addLayout(
            self._nav_buttons(lambda: self.stacked.setCurrentIndex(1), self._next_step)
        )

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
        self.label_storage_info = QLabel()
        self.label_storage_info.setWordWrap(True)
        self.label_storage_info.setObjectName("mutedLabel")
        self.label_total_payment = QLabel()
        self.label_total_payment.setObjectName("pageTitle")

        self.payment_method = QComboBox()
        self.payment_method.addItem("Tiền mặt", "cash")
        self.payment_method.addItem("Chuyển khoản", "bank_transfer")
        self.payment_method.addItem("Thẻ", "card")
        self.payment_method.addItem("Ví điện tử", "e_wallet")

        for caption, widget in [
            ("Gói tập chính", self.label_package_info),
            ("Hội viên", self.label_member_info),
            ("PT", self.label_trainer_info),
            ("Giá gói chính", self.label_price),
            ("Thời hạn", self.label_duration),
            ("Phí PT mua thêm", self.label_pt_fee_confirm),
            ("Phương thức", self.payment_method),
        ]:
            label = QLabel(caption)
            label.setObjectName("mutedLabel")
            layout.addWidget(label)
            layout.addWidget(widget)

        layout.addWidget(self.label_storage_info)
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
            self.selected_package = (
                self.session.query(Package).filter(Package.id == package_id).first()
            )

    def _next_step(self):
        current = self.stacked.currentIndex()
        if current == 0:
            if not self.selected_package:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn gói tập")
                return
            self.stacked.setCurrentIndex(1)
            return

        if current == 1:
            member_id = self.member_combo.currentData()
            if not member_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn hội viên")
                return
            self.selected_member = (
                self.session.query(Member).filter(Member.id == member_id).first()
            )
            self._configure_trainer_step()
            self.stacked.setCurrentIndex(2)
            return

        if current == 2:
            trainer_id = self.trainer_combo.currentData()
            self.selected_trainer = (
                self.session.query(Trainer).filter(Trainer.id == trainer_id).first()
                if trainer_id
                else None
            )
            package_type = self._selected_package_type()
            self.selected_pt_sessions = self.pt_package_combo.currentData() or 0

            if package_type in {"PT", "COMBO"} and self.selected_trainer is None:
                QMessageBox.warning(
                    self,
                    "Thiếu PT",
                    "Gói PT/COMBO bắt buộc phải chọn huấn luyện viên.",
                )
                return
            if package_type == "GYM" and self.selected_trainer and not self.selected_pt_sessions:
                QMessageBox.warning(
                    self,
                    "Thiếu số buổi PT",
                    "Đã chọn PT thì phải chọn gói 10/30/50/72 buổi.",
                )
                return

            self._update_confirm_page()
            self.stacked.setCurrentIndex(3)

    def _selected_package_type(self) -> str:
        return str(getattr(self.selected_package, "package_type", "GYM") or "GYM").upper()

    def _configure_trainer_step(self):
        package_type = self._selected_package_type()
        if package_type in {"PT", "COMBO"}:
            self.trainer_hint.setText(
                f"{package_type}: bắt buộc chọn PT. Số buổi lấy trực tiếp từ gói "
                f"({self.selected_package.sessions or 0} buổi)."
            )
            self.pt_package_combo.setCurrentIndex(0)
            self.pt_package_combo.setEnabled(False)
        else:
            self.trainer_hint.setText(
                "GYM: có thể không chọn PT, hoặc mua thêm 10/30/50/72 buổi PT. "
                "Hai số lượt được lưu riêng để Flutter không hiển thị sai."
            )
            self.pt_package_combo.setEnabled(bool(self.trainer_combo.currentData()))

    def _calculate_pt_fee(self) -> Decimal:
        if self._selected_package_type() in {"PT", "COMBO"}:
            return Decimal("0")
        trainer_selected = bool(self.trainer_combo.currentData())
        pt_count = self.pt_package_combo.currentData() or 0
        if trainer_selected and pt_count in self.PT_UNIT_PRICE:
            return Decimal(pt_count) * self.PT_UNIT_PRICE[pt_count]
        return Decimal("0")

    def _update_confirm_page(self):
        package_type = self._selected_package_type()
        pt_fee = self._calculate_pt_fee()
        base_price = Decimal(str(self.selected_package.price or 0))
        total_payment = base_price + pt_fee
        sessions_text = (
            str(self.selected_package.sessions)
            if self.selected_package.sessions is not None
            else "Không giới hạn"
        )

        self.label_package_info.setText(
            f"{self.selected_package.name} • {package_type} • {sessions_text}"
        )
        self.label_price.setText(format_money(base_price))
        self.label_duration.setText(f"{self.selected_package.duration_days} ngày")
        self.label_member_info.setText(
            f"{self.selected_member.user.full_name or self.selected_member.user.username} - "
            f"{self.selected_member.user.phone or 'N/A'}"
        )
        self.label_trainer_info.setText(
            self.selected_trainer.user.full_name if self.selected_trainer else "Không chọn"
        )
        self.label_pt_fee_confirm.setText(format_money(pt_fee))
        self.label_total_payment.setText(
            f"Tổng thanh toán: {format_money(total_payment)}"
        )

        if package_type == "GYM" and self.selected_trainer:
            self.label_storage_info.setText(
                "Hệ thống sẽ tạo 2 đăng ký độc lập: gói GYM giữ số lượt của gói "
                f"và gói PT giữ {self.selected_pt_sessions} buổi."
            )
        else:
            self.label_storage_info.setText(
                "Hệ thống sẽ lưu đầy đủ sessions_total, sessions_remaining, status, "
                "người tạo và chứng từ thanh toán."
            )

    def on_trainer_changed(self, _index):
        package_type = self._selected_package_type() if self.selected_package else "GYM"
        enabled = package_type == "GYM" and bool(self.trainer_combo.currentData())
        self.pt_package_combo.setEnabled(enabled)
        if not enabled:
            self.pt_package_combo.setCurrentIndex(0)
        self.on_pt_package_changed(self.pt_package_combo.currentIndex())

    def on_pt_package_changed(self, _index):
        self.selected_pt_sessions = self.pt_package_combo.currentData() or 0
        self.label_pt_fee.setText(
            f"Phí PT: {format_money(self._calculate_pt_fee())}"
        )

    def _ensure_pt_package(self, count: int) -> Package:
        total_price = Decimal(count) * self.PT_UNIT_PRICE[count]
        package = (
            self.session.query(Package)
            .filter(
                Package.package_type == "PT",
                Package.sessions == count,
                Package.is_active == True,  # noqa: E712
            )
            .order_by(Package.id.asc())
            .first()
        )
        if package:
            return package

        package = Package(
            name=f"Gói PT {count} Buổi",
            package_type="PT",
            description=(
                f"{count} buổi PT, đơn giá "
                f"{int(self.PT_UNIT_PRICE[count]):,} đồng/buổi."
            ),
            price=total_price,
            duration_days=self.PT_DURATION_DAYS[count],
            sessions=count,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.session.add(package)
        self.session.flush()
        return package

    def _expire_active_package_bucket(self, package_type: str, now: datetime) -> None:
        """Keep at most one active GYM bucket and one active PT bucket.

        is_active on packages only controls new sales. Existing member packages
        are expired here only when the member buys a replacement of the same
        business bucket.
        """
        normalized = str(package_type or "GYM").upper()
        if normalized == "COMBO":
            affected_types = ("GYM", "PT", "COMBO")
        elif normalized == "PT":
            affected_types = ("PT", "COMBO")
        else:
            affected_types = ("GYM", "COMBO")

        rows = (
            self.session.query(MemberPackage)
            .join(Package, Package.id == MemberPackage.package_id)
            .filter(
                MemberPackage.member_id == self.selected_member.id,
                MemberPackage.status == "active",
                MemberPackage.start_date <= now.date(),
                MemberPackage.end_date >= now.date(),
                Package.package_type.in_(affected_types),
            )
            .with_for_update()
            .all()
        )
        for row in rows:
            row.status = "expired"
            row.updated_at = now

    def _create_member_package(
        self,
        *,
        package: Package,
        start_date,
        end_date,
        trainer: Trainer | None,
        price_paid: Decimal,
        sessions_total: int | None,
        unit_price: Decimal | None,
    ) -> MemberPackage:
        record = MemberPackage(
            member_id=self.selected_member.id,
            package_id=package.id,
            start_date=start_date,
            end_date=end_date,
            sessions_total=sessions_total,
            sessions_remaining=sessions_total,
            pt_id=trainer.id if trainer else None,
            pt_session_unit_price=unit_price,
            price_paid=price_paid,
            status="active",
            created_by=self.current_user.id if self.current_user else None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.session.add(record)
        self.session.flush()
        return record

    def _create_payment_and_transaction(
        self,
        *,
        member_package: MemberPackage,
        amount: Decimal,
        description: str,
    ) -> None:
        now = datetime.now()
        payment = Payment(
            payment_code=(
                f"PAY-{now.strftime('%Y%m%d%H%M%S')}-"
                f"{uuid4().hex[:8].upper()}"
            ),
            member_id=self.selected_member.id,
            member_package_id=member_package.id,
            amount=amount,
            method=str(self.payment_method.currentData() or "cash"),
            status="paid",
            paid_at=now,
            confirmed_by=self.current_user.id if self.current_user else None,
            note=description,
            created_at=now,
        )
        self.session.add(payment)
        self.session.flush()

        self.session.add(
            Transaction(
                type="payment",
                amount=amount,
                date=now,
                description=description,
                created_by=self.current_user.id if self.current_user else None,
                reference_type="payment",
                reference_id=payment.id,
            )
        )

    def _confirm_registration(self):
        if not self.selected_package or not self.selected_member:
            QMessageBox.warning(self, "Lỗi", "Thông tin đăng ký chưa đầy đủ")
            return

        try:
            now = datetime.now()
            start_date = now.date()
            package_type = self._selected_package_type()
            base_price = Decimal(str(self.selected_package.price or 0))
            base_sessions = self.selected_package.sessions
            base_end_date = start_date + timedelta(
                days=int(self.selected_package.duration_days)
            )

            base_trainer = self.selected_trainer if package_type in {"PT", "COMBO"} else None
            base_unit_price = None
            if base_trainer and base_sessions:
                base_unit_price = (base_price / Decimal(base_sessions)).quantize(
                    Decimal("0.01")
                )

            self._expire_active_package_bucket(package_type, now)
            base_membership = self._create_member_package(
                package=self.selected_package,
                start_date=start_date,
                end_date=base_end_date,
                trainer=base_trainer,
                price_paid=base_price,
                sessions_total=base_sessions,
                unit_price=base_unit_price,
            )
            self._create_payment_and_transaction(
                member_package=base_membership,
                amount=base_price,
                description=(
                    f"Thanh toán {self.selected_package.name} cho "
                    f"{self.selected_member.user.full_name or self.selected_member.user.username}"
                ),
            )

            # Optional PT add-on for a GYM membership is stored separately.
            if package_type == "GYM" and self.selected_trainer and self.selected_pt_sessions:
                pt_count = int(self.selected_pt_sessions)
                pt_package = self._ensure_pt_package(pt_count)
                pt_fee = Decimal(pt_count) * self.PT_UNIT_PRICE[pt_count]
                pt_end_date = start_date + timedelta(
                    days=self.PT_DURATION_DAYS[pt_count]
                )
                self._expire_active_package_bucket("PT", now)
                pt_membership = self._create_member_package(
                    package=pt_package,
                    start_date=start_date,
                    end_date=pt_end_date,
                    trainer=self.selected_trainer,
                    price_paid=pt_fee,
                    sessions_total=pt_count,
                    unit_price=self.PT_UNIT_PRICE[pt_count],
                )
                self._create_payment_and_transaction(
                    member_package=pt_membership,
                    amount=pt_fee,
                    description=(
                        f"Thanh toán gói PT {pt_count} buổi cho "
                        f"{self.selected_member.user.full_name or self.selected_member.user.username}"
                    ),
                )

            self.selected_member.status = "active"
            self.selected_member.updated_at = now
            self.session.commit()
            QMessageBox.information(
                self,
                "Thành công",
                "Đăng ký gói thành công !",
            )
            self.accept()
        except Exception as exc:
            self.session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Đăng ký thất bại: {exc}")

    def closeEvent(self, event):
        self.session.close()
        super().closeEvent(event)
