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
from app.ui.tab_dashboard import TabDashboard
from app.ui.tab_history import TabHistory
from app.ui.tab_members import TabMembers
from app.ui.tab_packages import TabPackages
from app.ui.tab_qrdemo import TabQRDemo
from app.ui.tab_receptionists import TabReceptionists
from app.ui.tab_reports import TabReports
from app.ui.tab_trainers import TabTrainers
from app.ui.theme import APP_STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quản lý Phòng Gym")
        self.resize(1280, 780)
        self.setMinimumSize(1080, 680)
        self.nav_buttons = []

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
            ("Trang chủ", TabDashboard, False),
            ("Thử nghiệm QR", TabQRDemo, False),
            ("Lịch sử check-in", TabHistory, False),
            ("Lễ tân", TabReceptionists, True),
            ("Huấn luyện viên", TabTrainers, False),
            ("Gói tập", TabPackages, False),
            ("Hội viên", TabMembers, False),
            ("Doanh thu", TabReports, True),
        ]

        for title, factory, admin_only in pages:
            page = factory()
            self.stack.addWidget(page)
            button = self._build_nav_button(title, self.stack.count() - 1, admin_only)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()
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

    def set_current_page(self, index):
        button = self.nav_buttons[index]
        if not button.isEnabled():
            return
        self.stack.setCurrentIndex(index)
        for nav_button in self.nav_buttons:
            active = nav_button.property("page_index") == index
            nav_button.setChecked(active)
            nav_button.setProperty("active", active)
            nav_button.style().unpolish(nav_button)
            nav_button.style().polish(nav_button)

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
    app.setStyleSheet(APP_STYLESHEET)

    login = LoginDialog()

    if login.exec() == QDialog.DialogCode.Accepted:
        win = MainWindow()
        win.show()
        sys.exit(app.exec())

    sys.exit(0)


if __name__ == "__main__":
    main()
