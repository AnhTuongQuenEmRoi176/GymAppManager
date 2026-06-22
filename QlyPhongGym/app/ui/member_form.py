import os
import shutil
import uuid
from datetime import datetime

from PyQt6.QtWidgets import QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.auth import hash_password
from app.db import get_session
from app.models import Member, User
from app.ui.theme import page_title


class MemberForm(QDialog):
    def __init__(self, member_id=None):
        super().__init__()
        self.member_id = member_id
        self.setWindowTitle("Hội viên")
        self.resize(520, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(page_title("Thông tin hội viên", "Hồ sơ cá nhân và ảnh đại diện"))

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)

        self.name = QLineEdit()
        self.phone = QLineEdit()
        self.dob = QLineEdit()
        self.address = QLineEdit()
        self.avatar = QLineEdit()
        self.dob.setPlaceholderText("YYYY-MM-DD")
        self.btn_choose_avatar = QPushButton("Chọn ảnh")

        form = QFormLayout()
        form.addRow("Họ tên", self.name)
        form.addRow("SĐT", self.phone)
        form.addRow("Ngày sinh", self.dob)
        form.addRow("Địa chỉ", self.address)
        form.addRow("Ảnh đại diện", self.avatar)
        form.addRow("", self.btn_choose_avatar)
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
            self.dob.setText(member.dob.isoformat() if member.dob else "")
            self.address.setText(member.address or "")
            self.avatar.setText(member.user.avatar or "")
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

    def save(self):
        name = self.name.text().strip()
        phone = self.phone.text().strip()
        dob = self.dob.text().strip()
        address = self.address.text().strip()

        if not name:
            QMessageBox.warning(self, "Lỗi", "Họ tên không được để trống")
            return

        session = get_session()
        try:
            if self.member_id:
                member = session.query(Member).filter(Member.id == self.member_id).first()
                if not member:
                    QMessageBox.warning(self, "Lỗi", "Hội viên không tồn tại")
                    return
                user = member.user
            else:
                user = User(username=f"mem_{int(datetime.utcnow().timestamp())}", password_hash=hash_password("mem123"), full_name=name, phone=phone)
                session.add(user)
                session.flush()
                member = Member(user_id=user.id)
                session.add(member)

            user.full_name = name
            user.phone = phone
            member.address = address
            try:
                member.dob = datetime.fromisoformat(dob).date() if dob else None
            except Exception:
                QMessageBox.warning(self, "Lỗi", "Ngày sinh phải theo định dạng YYYY-MM-DD")
                return
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
