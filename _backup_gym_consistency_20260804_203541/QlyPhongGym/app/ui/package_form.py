from datetime import datetime

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
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

from app.db import get_session
from app.models import Package
from app.ui.theme import page_title
from app.ui.validators import parse_money, validate_required


class PackageForm(QDialog):
    """Create/edit a package using the same fields consumed by FastAPI."""

    def __init__(self, package_id=None):
        super().__init__()
        self.package_id = package_id
        self.setWindowTitle("Gói tập")
        self.resize(520, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(
            page_title(
                "Thông tin gói tập",
                "Loại gói, giá, thời hạn và số lượt sử dụng",
            )
        )

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)

        self.name = QLineEdit()
        self.package_type = QComboBox()
        self.package_type.addItem("GYM - Gói tập thông thường", "GYM")
        self.package_type.addItem("PT - Gói buổi với huấn luyện viên", "PT")
        self.package_type.addItem("COMBO - GYM kết hợp PT", "COMBO")
        self.description = QTextEdit()
        self.description.setMaximumHeight(90)
        self.price = QLineEdit()
        self.duration = QLineEdit()
        self.sessions = QLineEdit()
        self.is_active = QCheckBox("Cho phép đăng ký gói này")
        self.is_active.setChecked(True)

        self.name.setPlaceholderText("Ví dụ: Gói GYM 1 tháng 26 lượt")
        self.description.setPlaceholderText("Mô tả quyền lợi hoặc phạm vi sử dụng")
        self.price.setPlaceholderText("Ví dụ: 500000")
        self.duration.setPlaceholderText("Ví dụ: 30")
        self.sessions.setPlaceholderText("Để trống nếu không giới hạn")

        form = QFormLayout()
        form.addRow("Tên gói *", self.name)
        form.addRow("Loại gói *", self.package_type)
        form.addRow("Mô tả", self.description)
        form.addRow("Giá (VND) *", self.price)
        form.addRow("Thời hạn (ngày) *", self.duration)
        form.addRow("Số lượt/buổi", self.sessions)
        form.addRow("Trạng thái", self.is_active)
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
            package_type = (package.package_type or "GYM").upper()
            index = self.package_type.findData(package_type)
            self.package_type.setCurrentIndex(index if index >= 0 else 0)
            self.description.setPlainText(package.description or "")
            self.price.setText(str(package.price or ""))
            self.duration.setText(str(package.duration_days or ""))
            self.sessions.setText("" if package.sessions is None else str(package.sessions))
            self.is_active.setChecked(package.is_active is not False)
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
            if sessions is not None and sessions <= 0:
                raise ValueError("Số lượt/buổi phải lớn hơn 0 hoặc để trống")

            package_type = str(self.package_type.currentData() or "GYM").upper()
            if package_type in {"PT", "COMBO"} and sessions is None:
                raise ValueError("Gói PT/COMBO phải có số buổi cụ thể")
        except ValueError as exc:
            QMessageBox.warning(self, "Lỗi nhập liệu", str(exc))
            return None

        return {
            "name": name,
            "package_type": package_type,
            "description": self.description.toPlainText().strip() or None,
            "price": price,
            "duration_days": duration,
            "sessions": sessions,
            "is_active": self.is_active.isChecked(),
        }

    def save(self):
        values = self._validate()
        if not values:
            return

        session = get_session()
        try:
            if self.package_id:
                package = session.query(Package).filter(Package.id == self.package_id).first()
                if not package:
                    QMessageBox.warning(self, "Lỗi", "Gói không tồn tại")
                    return
            else:
                package = Package(created_at=datetime.now())
                session.add(package)

            for field, value in values.items():
                setattr(package, field, value)
            package.updated_at = datetime.now()

            session.commit()
            self.accept()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu gói tập: {exc}")
        finally:
            session.close()
