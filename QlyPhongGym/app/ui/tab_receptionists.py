from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.db import get_session
from app.models import Role, User
from app.state import is_admin
from app.ui.receptionist_form import ReceptionistForm
from app.ui.theme import configure_table, page_title


class TabReceptionists(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(page_title("Quản lý lễ tân", "Danh sách tài khoản vận hành quầy check-in"))

        toolbar = QFrame()
        toolbar.setObjectName("panel")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Tìm theo ID, SĐT hoặc tên")
        self.btn_search = QPushButton("Tìm")
        self.btn_add = QPushButton("Thêm lễ tân")
        self.btn_add.setObjectName("primaryButton")
        toolbar_layout.addWidget(self.search, 1)
        toolbar_layout.addWidget(self.btn_search)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_add)
        layout.addWidget(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Họ và tên", "SĐT"])
        configure_table(self.table)
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        self.btn_edit = QPushButton("Sửa")
        self.btn_delete = QPushButton("Xóa")
        self.btn_delete.setObjectName("dangerButton")
        actions.addStretch()
        actions.addWidget(self.btn_edit)
        actions.addWidget(self.btn_delete)
        layout.addLayout(actions)

        if not is_admin():
            for widget in (self.search, self.btn_search, self.btn_add, self.btn_edit, self.btn_delete):
                widget.setEnabled(False)
            note = QLabel("Bạn không có quyền truy cập chức năng này.")
            note.setObjectName("mutedLabel")
            layout.addWidget(note)

        self.btn_search.clicked.connect(self.refresh)
        self.search.returnPressed.connect(self.refresh)
        self.btn_add.clicked.connect(self.add_receptionist)
        self.btn_edit.clicked.connect(self.edit_receptionist)
        self.btn_delete.clicked.connect(self.delete_receptionist)
        self.refresh()

    def refresh(self):
        session = get_session()
        try:
            role = session.query(Role).filter(Role.name == "receptionist").first()
            if not role:
                self.table.setRowCount(0)
                return
            query = session.query(User).filter(User.role_id == role.id)
            term = self.search.text().strip()
            if term:
                query = query.filter(
                    (User.username.ilike(f"%{term}%")) |
                    (User.full_name.ilike(f"%{term}%")) |
                    (User.phone.ilike(f"%{term}%"))
                )
            users = query.order_by(User.id).all()
            self.table.setRowCount(len(users))
            for row, user in enumerate(users):
                values = [user.id, user.username, user.full_name or "", user.phone or ""]
                for col, value in enumerate(values):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
        finally:
            session.close()

    def selected_user_id(self):
        row = self.table.currentRow()
        if row < 0 or not self.table.item(row, 0):
            return None
        return int(self.table.item(row, 0).text())

    def add_receptionist(self):
        dlg = ReceptionistForm()
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def edit_receptionist(self):
        user_id = self.selected_user_id()
        if not user_id:
            QMessageBox.information(self, "Chú ý", "Chọn lễ tân để sửa")
            return
        dlg = ReceptionistForm(user_id=user_id)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def delete_receptionist(self):
        user_id = self.selected_user_id()
        if not user_id:
            QMessageBox.information(self, "Chú ý", "Chọn lễ tân để xóa")
            return
        if QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa lễ tân này?") != QMessageBox.StandardButton.Yes:
            return
        session = get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Xóa thất bại: {exc}")
        finally:
            session.close()
        self.refresh()

