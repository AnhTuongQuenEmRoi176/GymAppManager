from PyQt6.QtWidgets import QDialog, QFormLayout, QFrame, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.db import get_session
from app.models import Package
from app.ui.theme import page_title
from app.ui.validators import parse_money, validate_required


class PackageForm(QDialog):
    def __init__(self, package_id=None):
        super().__init__()
        self.package_id = package_id
        self.setWindowTitle("Gói tập")
        self.resize(460, 330)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(page_title("Thông tin gói tập", "Giá, thời hạn và số buổi sử dụng"))

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)

        self.name = QLineEdit()
        self.price = QLineEdit()
        self.duration = QLineEdit()
        self.sessions = QLineEdit()
        self.name.setPlaceholderText("Ví dụ: Gói 30 ngày")
        self.price.setPlaceholderText("Ví dụ: 500000")
        self.duration.setPlaceholderText("Số ngày")
        self.sessions.setPlaceholderText("Để trống nếu không giới hạn")

        form = QFormLayout()
        form.addRow("Tên gói *", self.name)
        form.addRow("Giá (VND) *", self.price)
        form.addRow("Thời hạn (ngày) *", self.duration)
        form.addRow("Số buổi", self.sessions)
        panel_layout.addLayout(form)

        buttons = QHBoxLayout()
        self.btn_save = QPushButton("Lưu")
        self.btn_save.setObjectName("primaryButton")
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setObjectName("ghostButton")
        buttons.addStretch()
        buttons.addWidget(self.btn_cancel)
        buttons.addWidget(self.btn_save)
        panel_layout.addLayout(buttons)
        layout.addWidget(panel)

        self.btn_save.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.reject)

        if self.package_id:
            self.load()

    def load(self):
        session = get_session()
        try:
            package = session.query(Package).filter(Package.id == self.package_id).first()
            if not package:
                return
            self.name.setText(package.name or "")
            self.price.setText(str(package.price or ""))
            self.duration.setText(str(package.duration_days or ""))
            self.sessions.setText(str(package.sessions or ""))
        finally:
            session.close()

    def _validate(self):
        name = self.name.text().strip()
        error = validate_required(name, "Tên gói")
        if error:
            QMessageBox.warning(self, "Lỗi nhập liệu", error)
            return None
        try:
            price = parse_money(self.price.text(), "Giá", required=True)
            duration = int(self.duration.text().strip())
            if duration <= 0:
                raise ValueError("Thời hạn phải lớn hơn 0")
            sessions_text = self.sessions.text().strip()
            sessions = int(sessions_text) if sessions_text else None
            if sessions is not None and sessions < 0:
                raise ValueError("Số buổi không được âm")
        except ValueError as exc:
            QMessageBox.warning(self, "Lỗi nhập liệu", str(exc))
            return None
        return name, price, duration, sessions

    def save(self):
        values = self._validate()
        if not values:
            return
        name, price, duration, sessions = values

        session = get_session()
        try:
            if self.package_id:
                package = session.query(Package).filter(Package.id == self.package_id).first()
                if not package:
                    QMessageBox.warning(self, "Lỗi", "Gói không tồn tại")
                    return
            else:
                package = Package()
                session.add(package)
            package.name = name
            package.price = price
            package.duration_days = duration
            package.sessions = sessions
            session.commit()
            self.accept()
        finally:
            session.close()
