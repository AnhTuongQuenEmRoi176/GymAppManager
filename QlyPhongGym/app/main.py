import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.state import get_current_user, is_admin
from app.ui.login import LoginDialog
from app.ui.theme import apply_app_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quản lý Phòng Gym")
        self.resize(1280, 780)
        self.setMinimumSize(1080, 680)
        self.nav_buttons = []
        self.page_specs = []
        self.loaded_pages = {}
        self.theme_mode = "dark"

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(248)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 18, 16, 16)
        sidebar_layout.setSpacing(8)

        logo = QLabel()
        logo.setObjectName("logoLabel")
        logo.setFixedSize(74, 74)
        logo_path = os.path.join(os.path.dirname(__file__), "resources", "branding", "gym_master_logo.png")
        if os.path.isfile(logo_path):
            logo.setPixmap(
                QPixmap(logo_path).scaled(
                    74,
                    74,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        sidebar_layout.addWidget(logo)

        brand = QLabel("Gym Master")
        brand.setObjectName("brandTitle")
        subtitle = QLabel("Quản trị vận hành")
        subtitle.setObjectName("brandSubTitle")
        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(12)

        self.stack = QStackedWidget()
        pages = [
            ("Trang chủ", "app.ui.tab_dashboard", "TabDashboard", False),
            ("Thử nghiệm QR", "app.ui.tab_qrdemo", "TabQRDemo", False),
            ("Lịch sử check-in", "app.ui.tab_history", "TabHistory", False),
            ("Lễ tân", "app.ui.tab_receptionists", "TabReceptionists", True),
            ("Huấn luyện viên", "app.ui.tab_trainers", "TabTrainers", False),
            ("Gói tập", "app.ui.tab_packages", "TabPackages", False),
            ("Hội viên", "app.ui.tab_members", "TabMembers", False),
            ("Doanh thu", "app.ui.tab_reports", "TabReports", True),
        ]

        for title, module_name, class_name, admin_only in pages:
            placeholder = QWidget()
            page_index = self.stack.addWidget(placeholder)
            self.page_specs.append((module_name, class_name))
            button = self._build_nav_button(title, page_index, admin_only)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()
        self.btn_theme = QPushButton("Chế độ sáng")
        self.btn_theme.setObjectName("secondaryButton")
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)

        user = get_current_user()
        user_text = user.full_name or user.username if user else "Chưa đăng nhập"
        role_text = "Admin" if is_admin() else "Lễ tân"
        current_user = QLabel(f"{user_text}\n{role_text}")
        current_user.setObjectName("brandSubTitle")
        current_user.setWordWrap(True)
        sidebar_layout.addWidget(current_user)

        content = QFrame()
        content.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.addWidget(self.stack)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(content, 1)
        self.setCentralWidget(root)

        self.apply_role_permissions()
        self.set_current_page(0)

    def _build_nav_button(self, title, index, admin_only=False):
        button = QPushButton(title)
        button.setObjectName("sidebarButton")
        button.setCheckable(True)
        button.setProperty("page_index", index)
        button.setProperty("admin_only", admin_only)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.clicked.connect(lambda: self.set_current_page(index))
        self.nav_buttons.append(button)
        return button

    def _ensure_page_loaded(self, index):
        if index in self.loaded_pages:
            return
        import importlib

        module_name, class_name = self.page_specs[index]
        module = importlib.import_module(module_name)
        page_class = getattr(module, class_name)
        page = page_class()
        old_widget = self.stack.widget(index)
        self.stack.removeWidget(old_widget)
        old_widget.deleteLater()
        self.stack.insertWidget(index, page)
        self.loaded_pages[index] = page

    def set_current_page(self, index):
        button = self.nav_buttons[index]
        if not button.isEnabled():
            return
        self._ensure_page_loaded(index)
        self.stack.setCurrentIndex(index)
        for nav_button in self.nav_buttons:
            active = nav_button.property("page_index") == index
            nav_button.setChecked(active)
            nav_button.setProperty("active", active)
            nav_button.style().unpolish(nav_button)
            nav_button.style().polish(nav_button)

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        apply_app_theme(QApplication.instance(), self.theme_mode)
        self.btn_theme.setText("Chế độ tối" if self.theme_mode == "light" else "Chế độ sáng")

    def apply_role_permissions(self):
        if is_admin():
            return
        for button in self.nav_buttons:
            if button.property("admin_only"):
                button.setEnabled(False)
                button.setText(f"{button.text()}  (Admin)")


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    apply_app_theme(app, "dark")

    login = LoginDialog()

    if login.exec() == QDialog.DialogCode.Accepted:
        win = MainWindow()
        win.show()
        sys.exit(app.exec())

    sys.exit(0)


if __name__ == "__main__":
    main()
