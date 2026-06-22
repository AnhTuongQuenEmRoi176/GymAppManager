import os
import shutil
import uuid
from datetime import datetime

from PyQt6.QtWidgets import QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.auth import hash_password
from app.db import get_session
from app.models import Member, User
from app.state import get_current_user
from app.ui.theme import page_title
from app.ui.validators import normalize_phone, parse_iso_date, validate_email, validate_phone, validate_required


DEFAULT_PASSWORD = "12345678"


class MemberForm(QDialog):
    def __init__(self, member_id=None):
        super().__init__()
        self.member_id = member_id
        self.setWindowTitle("Hội viên")
        self.resize(540, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(page_title("Thông tin hội viên", "Tài khoản mặc định dùng SĐT, mật khẩu 12345678"))

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)

        self.name = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.dob = QLineEdit()
        self.address = QLineEdit()
        self.avatar = QLineEdit()
        self.dob.setPlaceholderText("YYYY-MM-DD")
        self.phone.setPlaceholderText("VD: 0912345678")
        self.email.setPlaceholderText("Không bắt buộc")
        self.btn_choose_avatar = QPushButton("Chọn ảnh")
        self.btn_choose_avatar.setObjectName("secondaryButton")

        form = QFormLayout()
        form.addRow("Họ tên *", self.name)
        form.addRow("SĐT *", self.phone)
        form.addRow("Email", self.email)
        form.addRow("Ngày sinh", self.dob)
        form.addRow("Địa chỉ", self.address)
        form.addRow("Ảnh đại diện", self.avatar)
        form.addRow("", self.btn_choose_avatar)
        panel_layout.addLayout(form)

        self.meta_label = QLabel("Tài khoản mới: username = SĐT, mật khẩu = 12345678")
        self.meta_label.setObjectName("mutedLabel")
        panel_layout.addWidget(self.meta_label)

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
        self.btn_choose_avatar.clicked.connect(self.choose_avatar)

        if self.member_id:
            self.load()

    def load(self):
        session = get_session()
        try:
            member = session.query(Member).filter(Member.id == self.member_id).first()
            if not member:
                return
            self.name.setText(member.user.full_name or "")
            self.phone.setText(member.user.phone or "")
            self.email.setText(member.user.email or "")
            self.dob.setText(member.dob.isoformat() if member.dob else "")
            self.address.setText(member.address or "")
            self.avatar.setText(member.user.avatar or "")
            created_at = member.user.created_at.strftime("%d/%m/%Y %H:%M") if member.user.created_at else "Chưa rõ"
            self.meta_label.setText(f"Ngày thêm: {created_at} | Người thêm: chưa lưu trong schema hiện tại")
        finally:
            session.close()

    def _copy_avatar_if_needed(self, avatar_path, prefix):
        if not avatar_path:
            return ""
        resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "avatars")
        os.makedirs(resources_dir, exist_ok=True)
        if os.path.isfile(avatar_path) and not avatar_path.startswith(resources_dir):
            ext = os.path.splitext(avatar_path)[1]
            filename = f"{prefix}_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex}{ext}"
            destination = os.path.join(resources_dir, filename)
            shutil.copyfile(avatar_path, destination)
            return destination
        return avatar_path

    def _validate(self):
        name = self.name.text().strip()
        phone = normalize_phone(self.phone.text())
        email = self.email.text().strip()
        for error in (
            validate_required(name, "Họ tên"),
            validate_phone(phone),
            validate_email(email),
        ):
            if error:
                QMessageBox.warning(self, "Lỗi nhập liệu", error)
                return None
        try:
            dob = parse_iso_date(self.dob.text(), "Ngày sinh")
        except ValueError as exc:
            QMessageBox.warning(self, "Lỗi nhập liệu", str(exc))
            return None
        return name, phone, email, dob, self.address.text().strip()

    def save(self):
        values = self._validate()
        if not values:
            return
        name, phone, email, dob, address = values

        session = get_session()
        try:
            if self.member_id:
                member = session.query(Member).filter(Member.id == self.member_id).first()
                if not member:
                    QMessageBox.warning(self, "Lỗi", "Hội viên không tồn tại")
                    return
                duplicate = session.query(User).filter(User.username == phone, User.id != member.user_id).first()
                if duplicate:
                    QMessageBox.warning(self, "Lỗi", "SĐT này đã được dùng làm tài khoản khác")
                    return
                user = member.user
            else:
                if session.query(User).filter(User.username == phone).first():
                    QMessageBox.warning(self, "Lỗi", "SĐT này đã tồn tại, không thể dùng làm tài khoản mới")
                    return
                user = User(username=phone, password_hash=hash_password(DEFAULT_PASSWORD), full_name=name, phone=phone, email=email)
                session.add(user)
                session.flush()
                member = Member(user_id=user.id)
                session.add(member)

            user.username = phone
            user.full_name = name
            user.phone = phone
            user.email = email or None
            member.address = address
            member.dob = dob
            copied_avatar = self._copy_avatar_if_needed(self.avatar.text().strip(), "mem")
            if copied_avatar:
                user.avatar = copied_avatar
            session.commit()
            self.accept()
        finally:
            session.close()

    def choose_avatar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh đại diện", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.avatar.setText(path)
