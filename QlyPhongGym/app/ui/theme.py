from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QTableWidget


SURFACE = "#06111f"
SURFACE_LOW = "#0b1828"
SURFACE_CARD = "#101f31"
SURFACE_CARD_HIGH = "#18283a"
BORDER = "#26384b"
TEXT = "#e8f2ff"
TEXT_MUTED = "#94a3b8"
PRIMARY = "#ccff00"
PRIMARY_DARK = "#263500"
WARNING = "#ffb800"
ERROR = "#ff4d4d"
INFO = "#00d7ff"


def format_money(value):
    return f"{float(value or 0):,.0f} VND"


def page_title(text, subtitle=None):
    wrapper = QLabel(text if not subtitle else f"{text}\n{subtitle}")
    wrapper.setObjectName("pageTitle")
    wrapper.setWordWrap(True)
    return wrapper


def section_label(text):
    label = QLabel(text)
    label.setObjectName("sectionLabel")
    return label


def configure_table(table: QTableWidget):
    table.setAlternatingRowColors(True)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setShowGrid(False)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)
    table.setMinimumHeight(220)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(42)
    table.horizontalHeader().setMinimumSectionSize(86)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


APP_STYLESHEET = f"""
QWidget {{
    background: {SURFACE};
    color: {TEXT};
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background: {SURFACE};
}}

QFrame#sidebar {{
    background: #020a13;
    border-right: 1px solid {BORDER};
}}

QLabel#logoLabel {{
    background: transparent;
    border: 1px solid {BORDER};
    border-radius: 8px;
}}

QLabel#brandTitle {{
    color: {TEXT};
    font-size: 20px;
    font-weight: 800;
}}

QLabel#brandSubTitle, QLabel#mutedLabel {{
    color: {TEXT_MUTED};
}}

QPushButton#sidebarButton {{
    background: transparent;
    color: {TEXT_MUTED};
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 11px 13px;
    text-align: left;
    font-weight: 600;
}}

QPushButton#sidebarButton:hover {{
    background: {SURFACE_LOW};
    color: {TEXT};
}}

QPushButton#sidebarButton[active="true"] {{
    background: {PRIMARY};
    color: #152000;
    border-color: {PRIMARY};
}}

QFrame#contentFrame {{
    background: {SURFACE};
}}

QLabel#pageTitle {{
    color: {TEXT};
    font-size: 22px;
    font-weight: 800;
}}

QLabel#sectionLabel {{
    color: {TEXT};
    font-size: 15px;
    font-weight: 700;
}}

QFrame#panel, QGroupBox {{
    background: {SURFACE_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}

QGroupBox {{
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-weight: 700;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    color: {PRIMARY};
}}

QPushButton {{
    background: {SURFACE_CARD_HIGH};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 13px;
    font-weight: 700;
}}

QPushButton:hover:!disabled {{
    background: #20354d;
    border-color: #3b5874;
}}

QPushButton:disabled {{
    background: #172231;
    color: #64748b;
    border-color: #233244;
}}

QPushButton#primaryButton, QPushButton[variant="primary"] {{
    background: {PRIMARY};
    color: {PRIMARY_DARK};
    border-color: {PRIMARY};
}}

QPushButton#dangerButton, QPushButton[variant="danger"] {{
    background: #3a1720;
    color: #ffd6dc;
    border-color: #7f1d1d;
}}

QPushButton#ghostButton, QPushButton[variant="ghost"] {{
    background: transparent;
    color: {TEXT};
}}

QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {{
    background: {SURFACE_LOW};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 7px 9px;
    min-height: 22px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border-color: {PRIMARY};
}}

QComboBox::drop-down, QDateEdit::drop-down {{
    border: none;
    width: 24px;
}}

QTableWidget {{
    background: {SURFACE_CARD};
    alternate-background-color: #0c1a2a;
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: transparent;
    selection-background-color: #314716;
    selection-color: {TEXT};
}}

QTableWidget::item {{
    padding: 7px;
    border-bottom: 1px solid #17283a;
}}

QHeaderView::section {{
    background: #142338;
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 8px;
    font-weight: 800;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QSplitter::handle {{
    background: {BORDER};
}}

QFrame#statCard {{
    background: {SURFACE_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}

QLabel#statValue {{
    color: {PRIMARY};
    font-size: 21px;
    font-weight: 900;
}}

QLabel#statCaption {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 700;
}}

QFrame#trainerCard {{
    background: {SURFACE_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}

QFrame#trainerCard:hover {{
    border-color: #49637f;
    background: #142438;
}}
"""
