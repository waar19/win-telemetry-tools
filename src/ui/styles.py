"""
Styles Module
Contains QSS styles for the modern dark theme.
"""

# Color palette
COLORS = {
    "primary": "#6366f1",       # Indigo
    "primary_hover": "#818cf8",
    "primary_dark": "#4f46e5",
    "secondary": "#10b981",     # Emerald
    "secondary_hover": "#34d399",
    "danger": "#ef4444",        # Red
    "danger_hover": "#f87171",
    "warning": "#f59e0b",       # Amber
    "warning_hover": "#fbbf24",
    "success": "#22c55e",       # Green
    
    "bg_dark": "#0f0f0f",
    "bg_card": "#1a1a1a",
    "bg_input": "#252525",
    "bg_hover": "#2a2a2a",
    
    "text_primary": "#ffffff",
    "text_secondary": "#a1a1aa",
    "text_muted": "#71717a",
    
    "border": "#2e2e2e",
    "border_focus": "#6366f1",
}

# Main application stylesheet
MAIN_STYLESHEET = f"""
/* Global */
QWidget {{
    background-color: {COLORS["bg_dark"]};
    color: {COLORS["text_primary"]};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
}}

/* Main Window */
QMainWindow {{
    background-color: {COLORS["bg_dark"]};
}}

/* Scroll Areas */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {COLORS["bg_dark"]};
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS["border"]};
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["text_muted"]};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {COLORS["bg_dark"]};
    height: 8px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS["border"]};
    border-radius: 4px;
    min-width: 40px;
}}

/* Labels */
QLabel {{
    background-color: transparent;
    color: {COLORS["text_primary"]};
}}

QLabel#sectionTitle {{
    font-size: 20px;
    font-weight: bold;
    color: {COLORS["text_primary"]};
    padding: 8px 0;
}}

QLabel#subtitle {{
    font-size: 13px;
    color: {COLORS["text_secondary"]};
}}

QLabel#muted {{
    color: {COLORS["text_muted"]};
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS["primary"]};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
}}

QPushButton:hover {{
    background-color: {COLORS["primary_hover"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["primary_dark"]};
}}

QPushButton:disabled {{
    background-color: {COLORS["bg_input"]};
    color: {COLORS["text_muted"]};
}}

QPushButton#secondary {{
    background-color: transparent;
    border: 1px solid {COLORS["border"]};
    color: {COLORS["text_primary"]};
}}

QPushButton#secondary:hover {{
    background-color: {COLORS["bg_hover"]};
    border-color: {COLORS["text_muted"]};
}}

QPushButton#danger {{
    background-color: {COLORS["danger"]};
}}

QPushButton#danger:hover {{
    background-color: {COLORS["danger_hover"]};
}}

QPushButton#success {{
    background-color: {COLORS["secondary"]};
}}

QPushButton#success:hover {{
    background-color: {COLORS["secondary_hover"]};
}}

QPushButton#sidebar {{
    background-color: {COLORS["bg_input"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 14px 18px;
    text-align: left;
    font-weight: 500;
    font-size: 14px;
}}

QPushButton#sidebar:hover {{
    background-color: {COLORS["bg_hover"]};
    border-color: {COLORS["text_muted"]};
}}

QPushButton#sidebar:checked {{
    background-color: {COLORS["primary"]};
    border-color: {COLORS["primary"]};
    color: white;
}}

/* Cards */
QFrame#card {{
    background-color: {COLORS["bg_card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
    padding: 16px;
}}

QFrame#card:hover {{
    border-color: {COLORS["text_muted"]};
}}

/* Input fields */
QLineEdit {{
    background-color: {COLORS["bg_input"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLORS["text_primary"]};
}}

QLineEdit:focus {{
    border-color: {COLORS["border_focus"]};
}}

QLineEdit:disabled {{
    color: {COLORS["text_muted"]};
}}

/* Checkboxes */
QCheckBox {{
    spacing: 8px;
    color: {COLORS["text_primary"]};
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {COLORS["border"]};
    background-color: {COLORS["bg_input"]};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS["primary"]};
    border-color: {COLORS["primary"]};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS["primary"]};
}}

/* Toggle Switch (using checkbox) */
QCheckBox#toggle {{
    spacing: 12px;
}}

QCheckBox#toggle::indicator {{
    width: 44px;
    height: 24px;
    border-radius: 12px;
    border: none;
    background-color: {COLORS["bg_input"]};
}}

QCheckBox#toggle::indicator:checked {{
    background-color: {COLORS["primary"]};
}}

/* Tables */
QTableWidget {{
    background-color: {COLORS["bg_card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    gridline-color: {COLORS["border"]};
}}

QTableWidget::item {{
    padding: 8px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {COLORS["primary"]};
}}

QHeaderView::section {{
    background-color: {COLORS["bg_input"]};
    color: {COLORS["text_secondary"]};
    padding: 10px;
    border: none;
    font-weight: 600;
}}

/* Progress Bar */
QProgressBar {{
    background-color: {COLORS["bg_input"]};
    border: none;
    border-radius: 8px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS["primary"]};
    border-radius: 8px;
}}

/* Combo Box */
QComboBox {{
    background-color: {COLORS["bg_input"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLORS["text_primary"]};
}}

QComboBox:hover {{
    border-color: {COLORS["text_muted"]};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS["bg_card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    selection-background-color: {COLORS["primary"]};
}}

/* Message Box */
QMessageBox {{
    background-color: {COLORS["bg_card"]};
}}

QMessageBox QLabel {{
    color: {COLORS["text_primary"]};
}}

/* Tool Tips */
QToolTip {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px;
}}

/* Splitter */
QSplitter::handle {{
    background-color: {COLORS["border"]};
}}

QSplitter::handle:hover {{
    background-color: {COLORS["primary"]};
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    background-color: {COLORS["bg_card"]};
}}

QTabBar::tab {{
    background-color: {COLORS["bg_input"]};
    color: {COLORS["text_secondary"]};
    padding: 10px 20px;
    border: none;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
}}

QTabBar::tab:hover {{
    color: {COLORS["text_primary"]};
}}

/* Group Box */
QGroupBox {{
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {COLORS["text_primary"]};
}}
"""


def get_score_color(score: int) -> str:
    """Get color based on privacy score."""
    if score >= 80:
        return COLORS["success"]
    elif score >= 50:
        return COLORS["warning"]
    else:
        return COLORS["danger"]


def get_status_icon(is_protected: bool) -> str:
    """Get icon based on protection status."""
    return "✓" if is_protected else "✗"


def get_status_color(is_protected: bool) -> str:
    """Get color based on protection status."""
    return COLORS["success"] if is_protected else COLORS["danger"]
