from types import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.auth import generate_reset_token, hash_password, verify_password
from app.db import get_session
from app.models import Role, User
from app.state import set_current_user
from app.ui.theme import page_title
from app.ui.validators import normalize_phone, validate_phone, validate_required


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apex Gym - Đăng nhập")
        self.setModal(True)
        self.resize(460, 360)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(16)

        root.addWidget(page_title("Apex Gym", "Đăng nhập để bắt đầu ca làm việc"))

        panel = QFrame()
        panel.setObjectName("panel")
        form_layout = QVBoxLayout(panel)
        form_layout.setContentsMargins(22, 22, 22, 22)
        form_layout.setSpacing(12)

        form_layout.addWidget(QLabel("Tên đăng nhập"))
        self.username = QLineEdit()
        self.username.setPlaceholderText("Ví dụ: admin")
        form_layout.addWidget(self.username)

        form_layout.addWidget(QLabel("Mật khẩu"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Nhập mật khẩu")
        form_layout.addWidget(self.password)

        button_layout = QHBoxLayout()
        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.setObjectName("primaryButton")
        self.btn_register = QPushButton("Đăng ký lễ tân")
        self.btn_register.setObjectName("secondaryButton")
        self.btn_forgot = QPushButton("Quên mật khẩu")
        self.btn_forgot.setObjectName("warningButton")
        button_layout.addWidget(self.btn_login)
        button_layout.addWidget(self.btn_register)
        button_layout.addWidget(self.btn_forgot)
        form_layout.addLayout(button_layout)

        root.addWidget(panel)

        self.btn_login.clicked.connect(self.handle_login)
        self.btn_register.clicked.connect(self.handle_register)
        self.btn_forgot.clicked.connect(self.handle_forgot)
        self.password.returnPressed.connect(self.handle_login)

    def handle_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập và mật khẩu")
            return

        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                QMessageBox.warning(self, "Lỗi", "Người dùng không tồn tại")
                return
            if not verify_password(password, user.password_hash):
                QMessageBox.warning(self, "Lỗi", "Mật khẩu không chính xác")
                return

            role_name = None
            try:
                role_name = user.role.name
            except Exception:
                role_name = None

            lightweight = SimpleNamespace(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                phone=user.phone,
                email=user.email,
                avatar=user.avatar,
                role=SimpleNamespace(name=role_name),
            )
            set_current_user(lightweight)
            self.accept()
        finally:
            session.close()

    def handle_register(self):
        dlg = RegisterDialog()
        dlg.exec()

    def handle_forgot(self):
        username = self.username.text().strip()
        if not username:
            QMessageBox.information(self, "Quên mật khẩu", "Nhập tên đăng nhập để nhận mã reset demo")
            return
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                QMessageBox.warning(self, "Lỗi", "Người dùng không tồn tại")
                return
            token = generate_reset_token(user.email or user.username)
            QMessageBox.information(self, "Reset Token demo", f"Token: {token}")
        finally:
            session.close()


class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apex Gym - Đăng ký lễ tân")
        self.resize(480, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(page_title("Tài khoản lễ tân", "Admin duyệt cấu hình role trong dữ liệu"))

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.full_name = QLineEdit()
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("VD: 0912345678")
        form.addRow("Tên đăng nhập *", self.username)
        form.addRow("Mật khẩu *", self.password)
        form.addRow("Nhập lại mật khẩu *", self.confirm_password)
        form.addRow("Họ và tên *", self.full_name)
        form.addRow("Số điện thoại *", self.phone)
        panel_layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Đăng ký")
        self.btn_save.setObjectName("primaryButton")
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setObjectName("ghostButton")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        panel_layout.addLayout(btn_layout)
        layout.addWidget(panel)

        self.btn_save.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.reject)

    def save(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        confirm_password = self.confirm_password.text().strip()
        full_name = self.full_name.text().strip()
        phone = normalize_phone(self.phone.text())

        for error in (
            validate_required(username, "Tên đăng nhập"),
            validate_required(full_name, "Họ và tên"),
            validate_phone(phone),
        ):
            if error:
                QMessageBox.warning(self, "Lỗi nhập liệu", error)
                return
        if len(password) < 8:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Mật khẩu phải có ít nhất 8 ký tự")
            return
        if password != confirm_password:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Mật khẩu nhập lại không khớp")
            return

        session = get_session()
        try:
            if session.query(User).filter(User.username == username).first():
                QMessageBox.warning(self, "Lỗi", "Tên đăng nhập đã tồn tại")
                return
            if session.query(User).filter(User.phone == phone).first():
                QMessageBox.warning(self, "Lỗi", "Số điện thoại đã tồn tại")
                return
            role = session.query(Role).filter(Role.name == "receptionist").first()
            if not role:
                QMessageBox.warning(self, "Lỗi", "Role lễ tân chưa được cấu hình")
                return
            user = User(
                username=username,
                password_hash=hash_password(password),
                full_name=full_name,
                phone=phone,
                role_id=role.id,
            )
            session.add(user)
            session.commit()
            QMessageBox.information(self, "Thành công", "Đăng ký tài khoản thành công. Vui lòng đăng nhập.")
            self.accept()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi đăng ký: {exc}")
        finally:
            session.close()
