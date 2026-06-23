import os
from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.db import get_session
from app.models import Checkin, MemberPackage, PTSession, QRDemo, Trainer, User
from app.state import is_admin
from app.ui.theme import format_money, page_title
from app.ui.trainer_form import TrainerForm


class TabTrainers(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(page_title("Quản lý huấn luyện viên", "Theo dõi hồ sơ PT, KPI buổi dạy và gói đang phụ trách"))

        toolbar = QFrame()
        toolbar.setObjectName("panel")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm PT theo tên hoặc số điện thoại")
        self.btn_reload = QPushButton("↻")
        self.btn_reload.setObjectName("iconButton")
        self.btn_reload.setToolTip("T?i l?i danh s?ch")
        self.btn_add = QPushButton("Thêm PT mới")
        self.btn_add.setObjectName("primaryButton")
        toolbar_layout.addWidget(self.search_input, 1)
        toolbar_layout.addWidget(self.btn_reload)
        toolbar_layout.addWidget(self.btn_add)
        layout.addWidget(toolbar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.card_container = QWidget()
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(12)
        self.card_layout.addStretch()
        self.scroll_area.setWidget(self.card_container)
        layout.addWidget(self.scroll_area, 1)

        self.search_input.textChanged.connect(self.refresh)
        self.btn_reload.clicked.connect(self.refresh)
        self.btn_add.clicked.connect(self.add_trainer)
        self.refresh()

    def refresh(self):
        search_value = self.search_input.text().strip()
        session = get_session()
        try:
            query = session.query(Trainer).join(Trainer.user)
            if search_value:
                query = query.filter(
                    (User.full_name.ilike(f"%{search_value}%")) |
                    (User.phone.ilike(f"%{search_value}%"))
                )
            trainers = query.order_by(User.full_name).all()

            while self.card_layout.count() > 1:
                item = self.card_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            for trainer in trainers:
                card = self._build_trainer_card(session, trainer)
                self.card_layout.insertWidget(self.card_layout.count() - 1, card)

            if not trainers:
                empty_label = QLabel("Chưa có PT hoặc không tìm thấy kết quả.")
                empty_label.setObjectName("mutedLabel")
                self.card_layout.insertWidget(self.card_layout.count() - 1, empty_label)
        finally:
            session.close()

    def _avatar(self, path):
        label = QLabel("PT")
        label.setFixedSize(72, 72)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8; font-weight: 800;")
        if path and os.path.isfile(path):
            pix = QPixmap(path).scaled(
                72,
                72,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            label.setPixmap(pix)
        return label

    def _metric(self, caption, value):
        frame = QFrame()
        frame.setObjectName("statCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        label_value = QLabel(str(value))
        label_value.setObjectName("statValue")
        label_caption = QLabel(caption)
        label_caption.setObjectName("statCaption")
        layout.addWidget(label_value)
        layout.addWidget(label_caption)
        return frame

    def _build_trainer_card(self, session, trainer):
        frame = QFrame()
        frame.setObjectName("trainerCard")
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        layout.addWidget(self._avatar(trainer.user.avatar if trainer.user else None))

        info_layout = QVBoxLayout()
        name = QLabel(trainer.user.full_name or trainer.user.username or f"PT {trainer.id}")
        name.setObjectName("sectionLabel")
        subtitle = QLabel(f"SĐT: {trainer.user.phone or 'Chưa cập nhật'} | Email: {trainer.user.email or 'Chưa cập nhật'} | Bộ môn: {trainer.specialty or 'Chưa cập nhật'}")
        subtitle.setObjectName("mutedLabel")
        status = "Hoạt động" if (not trainer.end_date or trainer.end_date >= date.today()) else "Ngưng"
        meta = QLabel(
            f"Trạng thái: {status} | Ngày vào: {trainer.start_date or 'Chưa rõ'} | Ngày thêm: {trainer.user.created_at.strftime('%d/%m/%Y') if trainer.user.created_at else 'Chưa rõ'} | Lương cứng: {format_money(trainer.base_salary)}"
        )
        meta.setObjectName("mutedLabel")
        info_layout.addWidget(name)
        info_layout.addWidget(subtitle)
        info_layout.addWidget(meta)
        layout.addLayout(info_layout, 2)

        session_count = session.query(PTSession).filter(PTSession.trainer_id == trainer.id).count()
        active_packages = (
            session.query(MemberPackage)
            .filter(MemberPackage.pt_id == trainer.id, MemberPackage.end_date >= date.today())
            .count()
        )
        metrics = QHBoxLayout()
        metrics.addWidget(self._metric("Buổi đã dạy", session_count))
        metrics.addWidget(self._metric("Gói PT", active_packages))
        layout.addLayout(metrics, 1)

        buttons = QVBoxLayout()
        btn_detail = QPushButton("Chi tiết")
        btn_detail.setObjectName("secondaryButton")
        btn_edit = QPushButton("Sửa")
        btn_edit.setObjectName("warningButton")
        btn_resign = QPushButton("Cho nghỉ")
        btn_resign.setObjectName("warningButton")
        btn_delete = QPushButton("Xóa")
        btn_delete.setObjectName("dangerButton")
        if not is_admin():
            btn_resign.setEnabled(False)
            btn_delete.setEnabled(False)
        btn_detail.clicked.connect(lambda _, tid=trainer.id: self.open_detail(tid))
        btn_edit.clicked.connect(lambda _, tid=trainer.id: self.edit_trainer(tid))
        btn_resign.clicked.connect(lambda _, tid=trainer.id: self.resign_trainer(tid))
        btn_delete.clicked.connect(lambda _, tid=trainer.id: self.delete_trainer(tid))
        buttons.addWidget(btn_detail)
        buttons.addWidget(btn_edit)
        buttons.addWidget(btn_resign)
        buttons.addWidget(btn_delete)
        layout.addLayout(buttons)

        return frame

    def add_trainer(self):
        dlg = TrainerForm()
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def edit_trainer(self, trainer_id):
        dlg = TrainerForm(trainer_id=trainer_id)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def resign_trainer(self, trainer_id):
        if not is_admin():
            QMessageBox.warning(self, "Không có quyền", "Chỉ admin được cho PT thôi việc")
            return
        if QMessageBox.question(self, "X?c nh?n", "Cho PT n?y th?i vi?c? PT s? b? kh?a t?i kho?n nh?ng l?ch s? v?n ???c gi?.") != QMessageBox.StandardButton.Yes:
            return
        session = get_session()
        try:
            trainer = session.query(Trainer).filter(Trainer.id == trainer_id).first()
            if not trainer:
                return
            trainer.end_date = date.today()
            if trainer.user:
                trainer.user.is_active = False
            session.commit()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Cho thôi việc thất bại: {exc}")
        finally:
            session.close()
        self.refresh()

    def delete_trainer(self, trainer_id):
        if not is_admin():
            QMessageBox.warning(self, "Không có quyền", "Chỉ admin được xóa PT")
            return
        session = get_session()
        try:
            trainer = session.query(Trainer).filter(Trainer.id == trainer_id).first()
            if not trainer:
                return
            blockers = []
            if session.query(MemberPackage).filter(MemberPackage.pt_id == trainer.id).first():
                blockers.append("đã/đang quản lý gói PT")
            if session.query(PTSession).filter(PTSession.trainer_id == trainer.id).first():
                blockers.append("đã có buổi PT")
            if session.query(Checkin).filter(Checkin.trainer_id == trainer.id).first():
                blockers.append("đã có lịch sử check-in")
            if session.query(QRDemo).filter(QRDemo.entity_type == "trainer", QRDemo.entity_id == trainer.id).first():
                blockers.append("đã có mã QR demo")
            if blockers:
                QMessageBox.warning(self, "Không thể xóa", "PT còn ràng buộc: " + ", ".join(blockers) + ". Hãy dùng Cho nghỉ để khóa tài khoản.")
                return
            if QMessageBox.question(self, "X?c nh?n", "B?n c? ch?c mu?n x?a PT n?y?") != QMessageBox.StandardButton.Yes:
                return
            user = trainer.user
            session.delete(trainer)
            if user:
                session.delete(user)
            session.commit()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Xóa thất bại: {exc}")
        finally:
            session.close()
        self.refresh()

    def open_detail(self, trainer_id):
        from app.ui.trainer_detail import TrainerDetailDialog

        dlg = TrainerDetailDialog(trainer_id)
        dlg.exec()
