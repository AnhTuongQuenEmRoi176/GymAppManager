from PyQt6.QtWidgets import QDialog, QFormLayout, QFrame, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.auth import hash_password
from app.db import get_session
from app.models import Role, User
from app.ui.theme import page_title


class ReceptionistForm(QDialog):
    def __init__(self, user_id=None):
        super().__init__()
        self.setWindowTitle("Lễ tân")
        self.resize(460, 360)
        self.user_id = user_id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(page_title("Thông tin lễ tân", "Tài khoản dùng cho quầy check-in"))

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setPlaceholderText("Để trống nếu không đổi")
        self.full_name = QLineEdit()
        self.phone = QLineEdit()

        form = QFormLayout()
        form.addRow("Tên đăng nhập", self.username)
        form.addRow("Mật khẩu", self.password)
        form.addRow("Họ và tên", self.full_name)
        form.addRow("SĐT", self.phone)
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

        if self.user_id:
            self.load_user()

    def load_user(self):
        session = get_session()
        try:
            user = session.query(User).filter(User.id == self.user_id).first()
            if not user:
                QMessageBox.warning(self, "Lỗi", "Người dùng không tồn tại")
                self.reject()
                return
            self.username.setText(user.username)
            self.username.setEnabled(False)
            self.full_name.setText(user.full_name or "")
            self.phone.setText(user.phone or "")
        finally:
            session.close()

    def save(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        full_name = self.full_name.text().strip()
        phone = self.phone.text().strip()

        if not username:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập bắt buộc")
            return

        session = get_session()
        try:
            role = session.query(Role).filter(Role.name == "receptionist").first()
            if not role:
                QMessageBox.critical(self, "Lỗi", "Role receptionist chưa tồn tại")
                return

            if self.user_id:
                user = session.query(User).filter(User.id == self.user_id).first()
                if not user:
                    QMessageBox.warning(self, "Lỗi", "Người dùng không tồn tại")
                    return
                user.full_name = full_name
                user.phone = phone
                if password:
                    user.password_hash = hash_password(password)
            else:
                if session.query(User).filter(User.username == username).first():
                    QMessageBox.warning(self, "Lỗi", "Tên đăng nhập đã tồn tại")
                    return
                if not password:
                    QMessageBox.warning(self, "Lỗi", "Mật khẩu bắt buộc cho user mới")
                    return
                user = User(username=username, password_hash=hash_password(password), full_name=full_name, phone=phone, role_id=role.id)
                session.add(user)
            session.commit()
            QMessageBox.information(self, "Thành công", "Lưu thành công")
            self.accept()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Lỗi lưu: {exc}")
        finally:
            session.close()
