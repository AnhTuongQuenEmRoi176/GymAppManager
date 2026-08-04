from datetime import date

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.db import get_session
from app.models import MemberPackage, Package
from app.state import is_admin
from app.ui.package_form import PackageForm
from app.ui.package_registration import PackageRegistrationDialog
from app.ui.theme import configure_table, format_money, page_title


class TabPackages(QWidget):
    def __init__(self):
        super().__init__()
        self.sort_ascending = True
        self.search_term = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(
            page_title(
                "Quản lý gói tập",
                "Tạo gói, đăng ký gói và theo dõi số người đang dùng thực tế",
            )
        )

        toolbar = QFrame()
        toolbar.setObjectName("panel")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm theo tên hoặc loại gói")
        self.btn_search = QPushButton("Tìm")
        self.btn_search.setObjectName("secondaryButton")
        self.btn_sort = QPushButton("Giá tăng dần")
        self.btn_sort.setObjectName("secondaryButton")
        self.btn_reload = QPushButton("↻")
        self.btn_reload.setObjectName("iconButton")
        self.btn_reload.setToolTip("Tải lại danh sách từ database")
        self.btn_register = QPushButton("Đăng ký gói")
        self.btn_register.setObjectName("primaryButton")
        self.btn_add = QPushButton("Thêm gói")
        self.btn_add.setObjectName("successButton")

        toolbar_layout.addWidget(self.search_input, 1)
        toolbar_layout.addWidget(self.btn_search)
        toolbar_layout.addWidget(self.btn_sort)
        toolbar_layout.addWidget(self.btn_reload)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_register)
        toolbar_layout.addWidget(self.btn_add)
        layout.addWidget(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Tên gói",
                "Loại",
                "Giá",
                "Thời hạn",
                "Số lượt/buổi",
                "Đang dùng",
                "Trạng thái",
            ]
        )
        configure_table(self.table)
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        self.btn_edit = QPushButton("Sửa")
        self.btn_edit.setObjectName("warningButton")
        self.btn_delete = QPushButton("Ngừng sử dụng")
        self.btn_delete.setObjectName("dangerButton")
        actions.addStretch()
        actions.addWidget(self.btn_edit)
        actions.addWidget(self.btn_delete)
        layout.addLayout(actions)

        self.btn_search.clicked.connect(self.on_search)
        self.search_input.returnPressed.connect(self.on_search)
        self.btn_sort.clicked.connect(self.on_sort)
        self.btn_reload.clicked.connect(self.refresh)
        self.btn_register.clicked.connect(self.register_package)
        self.btn_add.clicked.connect(self.add_package)
        self.btn_edit.clicked.connect(self.edit_package)
        self.btn_delete.clicked.connect(self.deactivate_package)
        self.table.itemDoubleClicked.connect(self.edit_package)

        self.refresh()

    def on_search(self):
        self.search_term = self.search_input.text().strip()
        self.refresh()

    def on_sort(self):
        self.sort_ascending = not self.sort_ascending
        self.btn_sort.setText(
            "Giá tăng dần" if self.sort_ascending else "Giá giảm dần"
        )
        self.refresh()

    def refresh(self):
        session = get_session()
        try:
            query = session.query(Package)
            if self.search_term:
                like = f"%{self.search_term}%"
                query = query.filter(
                    (Package.name.ilike(like)) | (Package.package_type.ilike(like))
                )
            query = query.order_by(
                Package.price.asc() if self.sort_ascending else Package.price.desc(),
                Package.id.asc(),
            )
            packages = query.all()

            today = date.today()
            self.table.setRowCount(len(packages))
            for row, package in enumerate(packages):
                use_count = (
                    session.query(MemberPackage)
                    .filter(
                        MemberPackage.package_id == package.id,
                        MemberPackage.status == "active",
                        MemberPackage.start_date <= today,
                        MemberPackage.end_date >= today,
                    )
                    .count()
                )
                values = [
                    package.id,
                    package.name or "",
                    (package.package_type or "GYM").upper(),
                    format_money(package.price),
                    f"{package.duration_days} ngày",
                    package.sessions if package.sessions is not None else "Không giới hạn",
                    use_count,
                    "Đang mở" if package.is_active is not False else "Đã ngừng",
                ]
                for col, value in enumerate(values):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
        finally:
            session.close()

    def selected_package_id(self):
        row = self.table.currentRow()
        if row < 0 or not self.table.item(row, 0):
            return None
        return int(self.table.item(row, 0).text())

    def add_package(self):
        dialog = PackageForm()
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh()

    def register_package(self):
        dialog = PackageRegistrationDialog()
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh()

    def edit_package(self):
        package_id = self.selected_package_id()
        if not package_id:
            QMessageBox.information(self, "Chú ý", "Chọn gói để sửa")
            return
        dialog = PackageForm(package_id=package_id)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh()

    def deactivate_package(self):
        if not is_admin():
            QMessageBox.warning(
                self,
                "Không có quyền",
                "Chỉ Admin được thay đổi trạng thái gói tập.",
            )
            return

        package_id = self.selected_package_id()
        if not package_id:
            QMessageBox.information(self, "Chú ý", "Chọn gói cần ngừng sử dụng")
            return

        session = get_session()
        try:
            package = session.query(Package).filter(Package.id == package_id).first()
            if not package:
                return

            new_state = not bool(package.is_active)
            action = "mở lại" if new_state else "ngừng sử dụng"
            confirm = QMessageBox.question(
                self,
                "Xác nhận",
                f"Bạn có chắc muốn {action} gói '{package.name}'?\n"
                "Các đăng ký cũ vẫn được giữ nguyên.",
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

            package.is_active = new_state
            session.commit()
            self.refresh()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật gói: {exc}")
        finally:
            session.close()
