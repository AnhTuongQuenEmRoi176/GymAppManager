from datetime import date

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
from app.models import Member, MemberPackage, User
from app.ui.member_form import MemberForm
from app.ui.theme import configure_table, page_title


class TabMembers(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(page_title("Quản lý hội viên", "Theo dõi hồ sơ, gói tập và lịch sử check-in"))

        toolbar = QFrame()
        toolbar.setObjectName("panel")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm theo tên hoặc số điện thoại")
        self.btn_search = QPushButton("Tìm kiếm")
        self.btn_add = QPushButton("Thêm hội viên")
        self.btn_add.setObjectName("primaryButton")
        toolbar_layout.addWidget(self.search_input, 1)
        toolbar_layout.addWidget(self.btn_search)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_add)
        layout.addWidget(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Họ tên", "SĐT", "Trạng thái", "Gói đang dùng"])
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

        self.btn_add.clicked.connect(self.add_member)
        self.btn_edit.clicked.connect(self.edit_member)
        self.btn_delete.clicked.connect(self.delete_member)
        self.btn_search.clicked.connect(self.refresh)
        self.search_input.returnPressed.connect(self.refresh)
        self.table.itemDoubleClicked.connect(self.open_detail)

        self.refresh()

    def refresh(self):
        session = get_session()
        try:
            term = self.search_input.text().strip()
            query = session.query(Member).join(Member.user)
            if term:
                query = query.filter((User.full_name.ilike(f"%{term}%")) | (User.phone.ilike(f"%{term}%")))
            members = query.order_by(Member.id.desc()).all()
            self.table.setRowCount(len(members))
            for row, member in enumerate(members):
                active_packages = (
                    session.query(MemberPackage)
                    .filter(MemberPackage.member_id == member.id, MemberPackage.end_date >= date.today())
                    .count()
                )
                values = [
                    member.id,
                    member.user.full_name or member.user.username or "",
                    member.user.phone or "N/A",
                    member.status or "active",
                    active_packages,
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row, col, item)
        finally:
            session.close()

    def selected_member_id(self):
        row = self.table.currentRow()
        if row < 0 or not self.table.item(row, 0):
            return None
        return int(self.table.item(row, 0).text())

    def add_member(self):
        dlg = MemberForm()
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def edit_member(self):
        member_id = self.selected_member_id()
        if not member_id:
            QMessageBox.information(self, "Chú ý", "Chọn hội viên để sửa")
            return
        dlg = MemberForm(member_id=member_id)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def delete_member(self):
        member_id = self.selected_member_id()
        if not member_id:
            QMessageBox.information(self, "Chú ý", "Chọn hội viên để xóa")
            return
        if QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa hội viên này?") != QMessageBox.StandardButton.Yes:
            return
        session = get_session()
        try:
            member = session.query(Member).filter(Member.id == member_id).first()
            if member:
                user = member.user
                session.delete(member)
                if user:
                    session.delete(user)
                session.commit()
        finally:
            session.close()
        self.refresh()

    def open_detail(self, item):
        member_id = self.selected_member_id()
        if member_id:
            from app.ui.member_detail import MemberDetailDialog

            dlg = MemberDetailDialog(member_id)
            dlg.exec()

