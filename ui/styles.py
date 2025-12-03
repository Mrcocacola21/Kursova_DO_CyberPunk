"""
styles.py — Cyberpunk Neon (Qt-Compatible)
Жодних backdrop-filter / shadow — тільки валідні Qt-властивості.
"""

from __future__ import annotations
from dataclasses import dataclass

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QHeaderView,
    QGroupBox, QPushButton, QLabel
)

MARGIN = 12
SPACING = 10
RADIUS = 6

FONT_FAMILY = "Montserrat"
FONT_SIZE = 10

@dataclass(frozen=True)
class AppPalette:
    background: str = "#0b0f19"

    surface: str = "#111827"
    surface_alt: str = "#1f2937"

    text_main: str = "#EAF4FF"
    text_muted: str = "#8DA0C8"
    text_inverse: str = "#0b0f19"

    accent: str = "#7DF9FF"
    accent_strong: str = "#00E5FF"

    border: str = "#2D3A58"
    border_glow: str = "#00E5FF"

    success: str = "#00F5A8"
    warning: str = "#FFC600"
    error: str = "#FF3860"

PALETTE = AppPalette()


# ---------------------------------------------------------------------------
# GLOBAL APP STYLESHEET (Qt Compatible)
# ---------------------------------------------------------------------------

def build_app_stylesheet() -> str:
    p = PALETTE

    return f"""
    QWidget {{
        background-color: {p.background};
        color: {p.text_main};
        font-family: "{FONT_FAMILY}";
        font-size: {FONT_SIZE}pt;
    }}

    QMainWindow {{
        background-color: {p.background};
    }}

    /* Panels */
    QGroupBox {{
        background-color: {p.surface_alt};
        border: 1px solid {p.border};
        border-radius: {RADIUS}px;
        margin-top: 18px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 6px;
        color: {p.accent};
        font-weight: 600;
    }}

    /* Menu */
    QMenuBar {{
        background-color: {p.surface};
    }}
    QMenuBar::item:selected {{
        background-color: {p.accent_strong};
        color: {p.text_inverse};
        border-radius: 4px;
    }}

    QMenu {{
        background-color: {p.surface_alt};
        border: 1px solid {p.border};
    }}
    QMenu::item:selected {{
        background-color: {p.accent};
        color: {p.text_inverse};
    }}

    /* Status bar */
    QStatusBar {{
        background-color: {p.surface};
        color: {p.text_muted};
        border-top: 1px solid {p.border};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {p.accent};
        color: {p.text_inverse};
        border-radius: {RADIUS}px;
        padding: 7px 16px;
        border: 1px solid {p.accent_strong};
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {p.accent_strong};
    }}
    QPushButton:pressed {{
        background-color: {p.accent};
        border-color: {p.accent_strong};
    }}

    /* Inputs */
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: {RADIUS}px;
        padding: 6px;
        color: {p.text_main};
    }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border: 1px solid {p.accent};
    }}

    /* Checkboxes */
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 1px solid {p.border};
        background: {p.surface};
    }}
    QCheckBox::indicator:checked {{
        background: {p.accent};
        border: 1px solid {p.accent_strong};
    }}

    /* Tables */
    QTableWidget {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: {RADIUS}px;
        gridline-color: {p.border};
        alternate-background-color: {p.surface_alt};
    }}

    QHeaderView::section {{
        background-color: {p.surface_alt};
        color: {p.accent};
        padding: 6px;
        border: none;
        border-right: 1px solid {p.border};
        font-weight: 600;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background: transparent;
        width: 12px;
    }}
    QScrollBar::handle:vertical {{
        background: {p.accent_strong};
        border-radius: 6px;
    }}

    /* Tooltip */
    QToolTip {{
        background-color: {p.surface_alt};
        color: {p.text_main};
        border: 1px solid {p.accent_strong};
        padding: 6px;
        border-radius: 6px;
    }}
    """


# ---------------------------------------------------------------------------
# APPLY STYLE
# ---------------------------------------------------------------------------

def apply_app_style(app: QApplication) -> None:
    p = app.palette()

    p.setColor(QPalette.ColorRole.Window, QColor(PALETTE.background))
    p.setColor(QPalette.ColorRole.Base, QColor(PALETTE.surface))
    p.setColor(QPalette.ColorRole.Text, QColor(PALETTE.text_main))
    p.setColor(QPalette.ColorRole.Button, QColor(PALETTE.accent))

    app.setPalette(p)
    app.setFont(QFont(FONT_FAMILY, FONT_SIZE))
    app.setStyleSheet(build_app_stylesheet())


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def apply_groupbox_flat_style(group: QGroupBox):
    group.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)

def apply_table_style(table: QTableWidget):
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

def apply_button_secondary(btn: QPushButton):
    p = PALETTE
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {p.surface_alt};
            color: {p.text_main};
            border-radius: {RADIUS}px;
            padding: 6px 14px;
            border: 1px solid {p.border};
        }}
        QPushButton:hover {{
            border-color: {p.accent};
        }}
    """)

def apply_label_muted(lbl: QLabel):
    lbl.setStyleSheet(f"color: {PALETTE.text_muted};")

def apply_card_style(widget: QWidget):
    widget.setStyleSheet(f"""
        QWidget#{widget.objectName()} {{
            background-color: {PALETTE.surface};
            border-radius: {RADIUS}px;
            border: 1px solid {PALETTE.border};
        }}
    """)
