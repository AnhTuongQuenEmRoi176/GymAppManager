from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QTableWidget


DARK = {
    "surface": "#06111f",
    "surface_low": "#0b1828",
    "surface_card": "#101f31",
    "surface_high": "#18283a",
    "sidebar": "#020a13",
    "border": "#26384b",
    "text": "#e8f2ff",
    "muted": "#94a3b8",
    "primary": "#ccff00",
    "primary_text": "#1f2a00",
    "secondary": "#00d7ff",
    "warning": "#ffb800",
    "danger": "#ff4d4d",
    "success": "#29d391",
    "table_alt": "#0c1a2a",
    "selection": "#314716",
}

LIGHT = {
    "surface": "#f4f7fb",
    "surface_low": "#eef3f8",
    "surface_card": "#ffffff",
    "surface_high": "#e7eef6",
    "sidebar": "#0d1724",
    "border": "#d6e0ea",
    "text": "#142033",
    "muted": "#607086",
    "primary": "#9bd400",
    "primary_text": "#172000",
    "secondary": "#007f9e",
    "warning": "#b77900",
    "danger": "#c83349",
    "success": "#138a61",
    "table_alt": "#f7fafe",
    "selection": "#dff3a8",
}

SURFACE = DARK["surface"]
SURFACE_LOW = DARK["surface_low"]
SURFACE_CARD = DARK["surface_card"]
SURFACE_CARD_HIGH = DARK["surface_high"]
BORDER = DARK["border"]
TEXT = DARK["text"]
TEXT_MUTED = DARK["muted"]
PRIMARY = DARK["primary"]
PRIMARY_DARK = DARK["primary_text"]
WARNING = DARK["warning"]
ERROR = DARK["danger"]
INFO = DARK["secondary"]


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


def build_stylesheet(mode="dark"):
    c = LIGHT if mode == "light" else DARK
    return f"""
QWidget {{
    background: {c['surface']};
    color: {c['text']};
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 13px;
}}

QLabel {{
    background: transparent;
    border: none;
}}

QMainWindow, QDialog {{
    background: {c['surface']};
}}

QFrame#sidebar {{
    background: {c['sidebar']};
    border-right: 1px solid {c['border']};
}}

QLabel#logoLabel {{
    background: transparent;
    border: 1px solid {c['border']};
    border-radius: 8px;
}}

QLabel#brandTitle {{
    color: #ffffff;
    font-size: 20px;
    font-weight: 800;
}}

QLabel#brandSubTitle {{
    color: #9fb0c4;
}}

QLabel#mutedLabel {{
    color: {c['muted']};
}}

QPushButton#sidebarButton {{
    background: transparent;
    color: #aab8ca;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 11px 13px;
    text-align: left;
    font-weight: 650;
}}

QPushButton#sidebarButton:hover {{
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
}}

QPushButton#sidebarButton[active="true"] {{
    background: {c['primary']};
    color: {c['primary_text']};
    border-color: {c['primary']};
}}

QFrame#contentFrame {{
    background: {c['surface']};
}}

QLabel#pageTitle {{
    color: {c['text']};
    font-size: 23px;
    font-weight: 850;
    line-height: 30px;
}}

QLabel#sectionLabel {{
    color: {c['text']};
    font-size: 15px;
    font-weight: 750;
}}

QFrame#panel, QGroupBox {{
    background: {c['surface_card']};
    border: 1px solid {c['border']};
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
    color: {c['primary']};
    background: transparent;
}}

QFrame#topBar {{
    background: {c['surface_card']};
    border: 1px solid {c['border']};
    border-radius: 8px;
}}

QLabel#topBarTitle {{
    color: {c['text']};
    font-size: 18px;
    font-weight: 900;
}}

QLabel#topBarSubtitle {{
    color: {c['muted']};
    font-size: 12px;
    font-weight: 650;
}}

QPushButton#iconButton {{
    min-width: 34px;
    max-width: 34px;
    padding: 7px 0;
    background: {c['surface_high']};
    color: {c['primary']};
    border-color: {c['border']};
    font-size: 15px;
}}
QPushButton {{
    background: {c['surface_high']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 8px 13px;
    font-weight: 750;
}}

QPushButton:hover:!disabled {{
    border-color: {c['secondary']};
}}

QPushButton:pressed:!disabled {{
    padding-top: 9px;
    padding-bottom: 7px;
}}

QPushButton:disabled {{
    background: {c['surface_low']};
    color: {c['muted']};
    border-color: {c['border']};
}}

QPushButton#primaryButton, QPushButton[variant="primary"] {{
    background: {c['primary']};
    color: {c['primary_text']};
    border-color: {c['primary']};
}}

QPushButton#secondaryButton, QPushButton[variant="secondary"] {{
    background: {c['secondary']};
    color: #03131a;
    border-color: {c['secondary']};
}}

QPushButton#successButton, QPushButton[variant="success"] {{
    background: {c['success']};
    color: #03170f;
    border-color: {c['success']};
}}

QPushButton#warningButton, QPushButton[variant="warning"] {{
    background: {c['warning']};
    color: #1f1600;
    border-color: {c['warning']};
}}

QPushButton#dangerButton, QPushButton[variant="danger"] {{
    background: {c['danger']};
    color: #ffffff;
    border-color: {c['danger']};
}}

QPushButton#ghostButton, QPushButton[variant="ghost"] {{
    background: transparent;
    color: {c['text']};
}}

QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {{
    background: {c['surface_low']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 7px 9px;
    min-height: 22px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border-color: {c['primary']};
}}

QComboBox::drop-down, QDateEdit::drop-down {{
    border: none;
    width: 24px;
}}

QTableWidget {{
    background: {c['surface_card']};
    alternate-background-color: {c['table_alt']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    gridline-color: transparent;
    selection-background-color: {c['selection']};
    selection-color: {c['text']};
}}

QTableWidget::item {{
    padding: 7px;
    border-bottom: 1px solid {c['border']};
}}

QHeaderView::section {{
    background: {c['surface_high']};
    color: {c['muted']};
    border: none;
    border-bottom: 1px solid {c['border']};
    padding: 8px;
    font-weight: 850;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QSplitter::handle {{
    background: {c['border']};
}}

QFrame#statCard, QFrame#trainerCard {{
    background: {c['surface_card']};
    border: 1px solid {c['border']};
    border-radius: 8px;
}}

QFrame#trainerCard:hover {{
    border-color: {c['secondary']};
}}

QLabel#statValue {{
    color: {c['primary']};
    font-size: 21px;
    font-weight: 900;
}}

QLabel#statCaption {{
    color: {c['muted']};
    font-size: 12px;
    font-weight: 750;
}}
"""


def apply_app_theme(app, mode="dark"):
    app.setStyleSheet(build_stylesheet(mode))


APP_STYLESHEET = build_stylesheet("dark")
