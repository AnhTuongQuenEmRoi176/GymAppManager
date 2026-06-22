from PyQt6.QtWidgets import QDialog, QFormLayout, QFrame, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.db import get_session
from app.models import Package
from app.ui.theme import page_title


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
        form.addRow("Tên gói", self.name)
        form.addRow("Giá (VND)", self.price)
        form.addRow("Thời hạn (ngày)", self.duration)
        form.addRow("Số buổi", self.sessions)
        panel_layout.addLayout(form)

        buttons = QHBoxLayout()
        self.btn_save = QPushButton("Lưu")
        self.btn_save.setObjectName("primaryButton")
        self.btn_cancel = QPushButton("Hủy")
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

    def save(self):
        name = self.name.text().strip()
        price = self.price.text().strip() or "0"
        duration = self.duration.text().strip() or "0"
        sessions = self.sessions.text().strip() or None

        if not name:
            QMessageBox.warning(self, "Lỗi", "Tên gói không được để trống")
            return

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
            package.price = float(price)
            package.duration_days = int(duration)
            package.sessions = int(sessions) if sessions else None
            session.commit()
            self.accept()
        finally:
            session.close()
