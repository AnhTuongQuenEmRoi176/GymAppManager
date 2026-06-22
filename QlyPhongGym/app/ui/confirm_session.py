from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.ui.theme import page_title


class ConfirmSessionDialog(QDialog):
    def __init__(self, trainer, member):
        super().__init__()
        self.setWindowTitle("Xác nhận buổi tập")
        self.resize(460, 240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(page_title("Xác nhận buổi tập", "Ghi nhận KPI PT và trừ buổi hội viên"))

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.addWidget(QLabel(f"PT: {trainer.user.full_name} - SĐT: {trainer.user.phone or 'N/A'}"))
        panel_layout.addWidget(QLabel(f"Hội viên: {member.user.full_name} - SĐT: {member.user.phone or 'N/A'}"))

        buttons = QHBoxLayout()
        self.btn_cancel = QPushButton("Hủy")
        self.btn_confirm = QPushButton("Xác nhận")
        self.btn_confirm.setObjectName("primaryButton")
        buttons.addStretch()
        buttons.addWidget(self.btn_cancel)
        buttons.addWidget(self.btn_confirm)
        panel_layout.addLayout(buttons)
        layout.addWidget(panel)

        self.btn_confirm.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
