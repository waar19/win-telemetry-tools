"""
Dashboard Panel
Main overview panel showing privacy score and quick actions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGridLayout, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .styles import COLORS, get_score_color


class ScoreWidget(QWidget):
    """Large circular privacy score display."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._score = 0
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Score container
        self.score_label = QLabel("0")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Segoe UI", 72, QFont.Weight.Bold)
        self.score_label.setFont(font)
        self.score_label.setStyleSheet(f"color: {get_score_color(0)};")
        
        # Score subtitle
        self.subtitle_label = QLabel("Privacy Score")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setObjectName("subtitle")
        
        # Status text
        self.status_label = QLabel("Your privacy needs attention")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("muted")
        
        layout.addWidget(self.score_label)
        layout.addWidget(self.subtitle_label)
        layout.addSpacing(8)
        layout.addWidget(self.status_label)
    
    def set_score(self, score: int):
        self._score = score
        self.score_label.setText(str(score))
        self.score_label.setStyleSheet(f"color: {get_score_color(score)};")
        
        if score >= 80:
            status = "Excellent! Your privacy is well protected"
        elif score >= 60:
            status = "Good, but there's room for improvement"
        elif score >= 40:
            status = "Your privacy needs some attention"
        else:
            status = "Warning: Your privacy is at risk"
        
        self.status_label.setText(status)


class StatCard(QFrame):
    """Small card showing a single statistic."""
    
    clicked = pyqtSignal()
    
    def __init__(self, title: str, value: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui(title, value, icon)
    
    def _setup_ui(self, title: str, value: str, icon: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header with icon
        header = QHBoxLayout()
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px;")
            header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setObjectName("subtitle")
        header.addWidget(title_label)
        header.addStretch()
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        
        layout.addLayout(header)
        layout.addWidget(self.value_label)
    
    def set_value(self, value: str):
        self.value_label.setText(value)
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class QuickActionCard(QFrame):
    """Card with a quick action button."""
    
    action_clicked = pyqtSignal(str)
    
    def __init__(self, title: str, description: str, action_text: str, 
                 action_id: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.action_id = action_id
        self.setObjectName("card")
        self._setup_ui(title, description, action_text, icon)
    
    def _setup_ui(self, title: str, description: str, action_text: str, icon: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Header
        header = QHBoxLayout()
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 28px;")
            header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(title_label)
        header.addStretch()
        
        # Description
        desc_label = QLabel(description)
        desc_label.setObjectName("muted")
        desc_label.setWordWrap(True)
        
        # Action button
        self.action_btn = QPushButton(action_text)
        self.action_btn.clicked.connect(lambda: self.action_clicked.emit(self.action_id))
        
        layout.addLayout(header)
        layout.addWidget(desc_label)
        layout.addWidget(self.action_btn)


class DashboardPanel(QWidget):
    """Main dashboard panel with privacy overview."""
    
    navigate_to = pyqtSignal(str)
    action_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(32, 32, 32, 32)
        
        # Title
        title = QLabel("Privacy Dashboard")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Score widget
        self.score_widget = ScoreWidget()
        layout.addWidget(self.score_widget)
        
        # Stats grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)
        
        self.telemetry_stat = StatCard("Telemetry", "0%", "📡")
        self.telemetry_stat.clicked.connect(lambda: self.navigate_to.emit("telemetry"))
        
        self.permissions_stat = StatCard("Permissions", "0%", "🔐")
        self.permissions_stat.clicked.connect(lambda: self.navigate_to.emit("permissions"))
        
        self.firewall_stat = StatCard("Firewall", "0/0", "🛡️")
        self.firewall_stat.clicked.connect(lambda: self.navigate_to.emit("firewall"))
        
        self.cleanup_stat = StatCard("Cleanup", "0 MB", "🧹")
        self.cleanup_stat.clicked.connect(lambda: self.navigate_to.emit("cleanup"))
        
        stats_layout.addWidget(self.telemetry_stat, 0, 0)
        stats_layout.addWidget(self.permissions_stat, 0, 1)
        stats_layout.addWidget(self.firewall_stat, 1, 0)
        stats_layout.addWidget(self.cleanup_stat, 1, 1)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 16px;")
        layout.addWidget(actions_title)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)
        
        protect_card = QuickActionCard(
            "Maximum Protection",
            "Block all telemetry, disable permissions, and add firewall rules",
            "Enable All",
            "protect_all",
            "🛡️"
        )
        protect_card.action_clicked.connect(self.action_requested.emit)
        
        cleanup_card = QuickActionCard(
            "Quick Cleanup",
            "Clear tracking data, caches, and reset advertising ID",
            "Clean Now",
            "cleanup_all",
            "🧹"
        )
        cleanup_card.action_clicked.connect(self.action_requested.emit)
        
        actions_layout.addWidget(protect_card)
        actions_layout.addWidget(cleanup_card)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
    
    def update_scores(self, telemetry: int, permissions: int, 
                      firewall: tuple, cleanup_size: int):
        """Update all stat cards with current values."""
        # Calculate overall score
        firewall_score = (firewall[0] / firewall[1] * 100) if firewall[1] > 0 else 0
        overall = int((telemetry + permissions + firewall_score) / 3)
        
        self.score_widget.set_score(overall)
        self.telemetry_stat.set_value(f"{telemetry}%")
        self.permissions_stat.set_value(f"{permissions}%")
        self.firewall_stat.set_value(f"{firewall[0]}/{firewall[1]}")
        
        # Format cleanup size
        if cleanup_size > 1024 * 1024 * 1024:
            size_str = f"{cleanup_size / (1024*1024*1024):.1f} GB"
        elif cleanup_size > 1024 * 1024:
            size_str = f"{cleanup_size / (1024*1024):.1f} MB"
        elif cleanup_size > 1024:
            size_str = f"{cleanup_size / 1024:.1f} KB"
        else:
            size_str = f"{cleanup_size} B"
        
        self.cleanup_stat.set_value(size_str)
