import os
import shutil
import uuid
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.db import get_session
from app.models import Member, QRDemo, Trainer
from app.ui.theme import configure_table, page_title


class TabQRDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.session = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(page_title("Thử nghiệm QR", "Tạo mã QR demo cho hội viên và PT"))

        controls_panel = QFrame()
        controls_panel.setObjectName("panel")
        controls = QHBoxLayout(controls_panel)
        controls.setContentsMargins(16, 14, 16, 14)
        self.type_combo = QComboBox()
        self.type_combo.addItem("Hội viên", "member")
        self.type_combo.addItem("PT", "trainer")
        self.entity_combo = QComboBox()
        self.btn_create = QPushButton("Tạo mã QR")
        self.btn_create.setObjectName("primaryButton")
        self.btn_export = QPushButton("Xuất mã QR")
        self.btn_export.setObjectName("secondaryButton")
        controls.addWidget(self.type_combo)
        controls.addWidget(self.entity_combo, 1)
        controls.addWidget(self.btn_create)
        controls.addWidget(self.btn_export)
        layout.addWidget(controls_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Code", "Loại", "Đối tượng", "Tạo lúc"])
        configure_table(self.table)
        splitter.addWidget(self.table)

        preview_panel = QFrame()
        preview_panel.setObjectName("panel")
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(16, 16, 16, 16)
        preview_layout.addWidget(QLabel("Preview"))
        self.preview_label = QLabel("Chọn một mã để xem trước")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_label.setMinimumWidth(300)
        self.preview_label.setStyleSheet("border: 1px solid #26384b; border-radius: 8px; background: #020a13; color: #94a3b8;")
        preview_layout.addWidget(self.preview_label, 1)
        splitter.addWidget(preview_panel)
        splitter.setSizes([760, 360])
        layout.addWidget(splitter, 1)

        self.type_combo.currentIndexChanged.connect(self.load_entities)
        self.btn_create.clicked.connect(self.create_qr)
        self.btn_export.clicked.connect(self.export_selected)
        self.table.itemSelectionChanged.connect(self.on_table_select)

        self.load_entities()
        self.load_qrdemos()

    def get_session(self):
        if not self.session:
            self.session = get_session()
        return self.session

    def _qr_resources_dir(self):
        resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "qr_demo")
        os.makedirs(resources_dir, exist_ok=True)
        return resources_dir

    def load_entities(self):
        self.entity_combo.clear()
        session = self.get_session()
        entity_type = self.type_combo.currentData()
        if entity_type == "member":
            for member in session.query(Member).all():
                self.entity_combo.addItem(f"{member.user.full_name} ({member.user.username})", member.id)
        else:
            for trainer in session.query(Trainer).all():
                self.entity_combo.addItem(f"{trainer.user.full_name} ({trainer.user.username})", trainer.id)

    def load_qrdemos(self):
        session = self.get_session()
        demos = session.query(QRDemo).order_by(QRDemo.created_at.desc()).all()
        self.table.setRowCount(len(demos))
        for row, demo in enumerate(demos):
            name = ""
            if demo.entity_type == "member":
                member = session.query(Member).filter(Member.id == demo.entity_id).first()
                name = member.user.full_name if member else ""
            else:
                trainer = session.query(Trainer).filter(Trainer.id == demo.entity_id).first()
                name = trainer.user.full_name if trainer else ""
            values = [demo.id, demo.code, demo.entity_type, name, demo.created_at]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def create_qr(self):
        entity_type = self.type_combo.currentData()
        entity_id = self.entity_combo.currentData()
        if not entity_id:
            QMessageBox.warning(self, "Lỗi", "Chọn đối tượng để tạo QR")
            return

        payload = f"{entity_type}:{entity_id}"
        try:
            import qrcode
        except Exception:
            QMessageBox.critical(self, "Lỗi", "Thiếu thư viện qrcode. Cài đặt bằng pip install qrcode")
            return

        session = self.get_session()
        session.rollback()

        try:
            existing = session.query(QRDemo).filter(QRDemo.code == payload).first()
            found_file = self._find_qr_file(payload)
            if found_file:
                filepath = found_file
            else:
                filename = f"{entity_type}_{entity_id}_{uuid.uuid4().hex}.png"
                filepath = os.path.join(self._qr_resources_dir(), filename)
                qrcode.make(payload).save(filepath)

            if existing:
                self.load_qrdemos()
                self._select_code(payload)
                QMessageBox.information(
                    self,
                    "Mã QR đã tồn tại",
                    f"Đã có mã QR cho {payload}. App sẽ dùng lại mã hiện có.\nFile: {filepath}",
                )
                return

            demo = QRDemo(code=payload, entity_type=entity_type, entity_id=entity_id, created_at=datetime.utcnow())
            session.add(demo)
            session.commit()
            self.load_qrdemos()
            self._select_code(payload)
            QMessageBox.information(self, "Tạo thành công", f"Đã tạo QR cho {payload}\nLưu tại: {filepath}")
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Lỗi", f"Tạo QR thất bại: {exc}")

    def _find_qr_file(self, code):
        prefix = code.replace(":", "_")
        resources_dir = self._qr_resources_dir()
        for filename in os.listdir(resources_dir):
            if filename.startswith(prefix):
                return os.path.join(resources_dir, filename)
        return None

    def _select_code(self, code):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item and item.text() == code:
                self.table.selectRow(row)
                self.on_table_select()
                return

    def on_table_select(self):
        row = self.table.currentRow()
        if row < 0 or not self.table.item(row, 1):
            return
        code = self.table.item(row, 1).text()
        found = self._find_qr_file(code)
        if found and os.path.isfile(found):
            pix = QPixmap(found).scaled(320, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(pix)
        else:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("Không tìm thấy file QR")

    def export_selected(self):
        row = self.table.currentRow()
        if row < 0 or not self.table.item(row, 1):
            QMessageBox.information(self, "Chú ý", "Chọn mã QR để xuất")
            return
        code = self.table.item(row, 1).text()
        found = self._find_qr_file(code)
        if not found:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file QR để xuất")
            return

        dest, _ = QFileDialog.getSaveFileName(self, "Lưu QR", f"{code}.png", "PNG Files (*.png)")
        if dest:
            try:
                shutil.copyfile(found, dest)
                QMessageBox.information(self, "Hoàn tất", f"Đã xuất sang {dest}")
            except Exception as exc:
                QMessageBox.critical(self, "Lỗi", f"Xuất thất bại: {exc}")


