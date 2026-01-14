"""
Dashboard Panel
Main panel with privacy score, stats, and score history.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath

from .styles import COLORS, get_score_color
from ..i18n import tr
from ..modules.score_history import ScoreHistory


class ScoreHistoryWidget(QFrame):
    """Mini chart showing score history."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(100)
        self.setMaximumHeight(120)
        self._history = []
        self._trend = "stable"
    
    def set_history(self, history: list, trend: str):
        """Set history data for display."""
        self._history = history
        self._trend = trend
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self._history:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw area
        margin = 20
        width = self.width() - (margin * 2)
        height = self.height() - (margin * 2)
        
        if len(self._history) < 2:
            return
        
        # Calculate points
        scores = [e.score for e in self._history]
        min_score = max(0, min(scores) - 10)
        max_score = min(100, max(scores) + 10)
        score_range = max_score - min_score if max_score != min_score else 1
        
        points = []
        for i, score in enumerate(scores):
            x = margin + (i / (len(scores) - 1)) * width
            y = margin + height - ((score - min_score) / score_range) * height
            points.append((x, y))
        
        # Draw line
        pen = QPen(QColor(COLORS["primary"]))
        pen.setWidth(2)
        painter.setPen(pen)
        
        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.lineTo(x, y)
        
        painter.drawPath(path)
        
        # Draw dots
        painter.setBrush(QColor(COLORS["primary"]))
        for x, y in points:
            painter.drawEllipse(int(x) - 4, int(y) - 4, 8, 8)
        
        # Draw trend indicator
        trend_color = COLORS["success"] if self._trend == "up" else COLORS["danger"] if self._trend == "down" else COLORS["text_muted"]
        trend_text = "↑" if self._trend == "up" else "↓" if self._trend == "down" else "→"
        
        painter.setPen(QColor(trend_color))
        painter.setFont(self.font())
        painter.drawText(self.width() - 30, 25, trend_text)


class DashboardPanel(QWidget):
    """Main dashboard with privacy overview."""
    
    navigate_to = pyqtSignal(str)
    action_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.score_history = ScoreHistory()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        self.title = QLabel(tr("dashboard.title"))
        self.title.setObjectName("sectionTitle")
        layout.addWidget(self.title)
        
        # Privacy Score Section
        score_frame = QFrame()
        score_frame.setObjectName("card")
        score_layout = QHBoxLayout(score_frame)
        score_layout.setContentsMargins(24, 24, 24, 24)
        
        # Score Circle
        score_container = QVBoxLayout()
        self.score_label = QLabel("--")
        self.score_label.setStyleSheet(f"""
            font-size: 64px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.score_title = QLabel(tr("dashboard.privacy_score"))
        self.score_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.score_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        score_container.addWidget(self.score_label)
        score_container.addWidget(self.score_title)
        
        # Score Description
        desc_container = QVBoxLayout()
        self.score_desc = QLabel(tr("dashboard.excellent"))
        self.score_desc.setWordWrap(True)
        self.score_desc.setStyleSheet("font-size: 15px;")
        desc_container.addWidget(self.score_desc)
        desc_container.addStretch()
        
        score_layout.addLayout(score_container)
        score_layout.addSpacing(40)
        score_layout.addLayout(desc_container, stretch=1)
        
        layout.addWidget(score_frame)
        
        # Score History Chart
        history_header = QHBoxLayout()
        self.history_title = QLabel("Score History (7 days)")
        self.history_title.setStyleSheet("font-weight: bold;")
        history_header.addWidget(self.history_title)
        history_header.addStretch()
        layout.addLayout(history_header)
        
        self.history_chart = ScoreHistoryWidget()
        layout.addWidget(self.history_chart)
        
        # Stats Grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        
        self.stat_cards = {}
        self.stat_cards["telemetry"] = self._create_stat_card(tr("nav.telemetry"), "0%", "blocked")
        self.stat_cards["permissions"] = self._create_stat_card(tr("nav.permissions"), "0%", "restricted")
        self.stat_cards["firewall"] = self._create_stat_card(tr("nav.firewall"), "0/0", "blocked")
        self.stat_cards["cleanup"] = self._create_stat_card(tr("nav.cleanup"), "0 MB", "to clean")
        
        stats_grid.addWidget(self.stat_cards["telemetry"], 0, 0)
        stats_grid.addWidget(self.stat_cards["permissions"], 0, 1)
        stats_grid.addWidget(self.stat_cards["firewall"], 1, 0)
        stats_grid.addWidget(self.stat_cards["cleanup"], 1, 1)
        
        layout.addLayout(stats_grid)
        
        # Quick Actions
        self.actions_title = QLabel(tr("dashboard.quick_actions"))
        self.actions_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 16px;")
        layout.addWidget(self.actions_title)
        
        actions_layout = QHBoxLayout()
        
        # Max Protection Card
        protect_card = QFrame()
        protect_card.setObjectName("card")
        protect_layout = QVBoxLayout(protect_card)
        
        self.protect_title = QLabel(tr("dashboard.max_protection"))
        self.protect_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.protect_desc = QLabel(tr("dashboard.max_protection_desc"))
        self.protect_desc.setObjectName("muted")
        self.protect_desc.setWordWrap(True)
        
        self.protect_btn = QPushButton(tr("dashboard.enable_all"))
        self.protect_btn.clicked.connect(lambda: self.action_requested.emit("protect_all"))
        
        protect_layout.addWidget(self.protect_title)
        protect_layout.addWidget(self.protect_desc)
        protect_layout.addStretch()
        protect_layout.addWidget(self.protect_btn)
        
        # Cleanup Card
        cleanup_card = QFrame()
        cleanup_card.setObjectName("card")
        cleanup_layout = QVBoxLayout(cleanup_card)
        
        self.cleanup_title = QLabel(tr("dashboard.quick_cleanup"))
        self.cleanup_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.cleanup_desc = QLabel(tr("dashboard.quick_cleanup_desc"))
        self.cleanup_desc.setObjectName("muted")
        self.cleanup_desc.setWordWrap(True)
        
        self.cleanup_btn = QPushButton(tr("dashboard.clean_now"))
        self.cleanup_btn.setObjectName("secondary")
        self.cleanup_btn.clicked.connect(lambda: self.action_requested.emit("cleanup_all"))
        
        cleanup_layout.addWidget(self.cleanup_title)
        cleanup_layout.addWidget(self.cleanup_desc)
        cleanup_layout.addStretch()
        cleanup_layout.addWidget(self.cleanup_btn)
        
        actions_layout.addWidget(protect_card)
        actions_layout.addWidget(cleanup_card)
        
        layout.addLayout(actions_layout)
    
    def _create_stat_card(self, title: str, value: str, subtitle: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setObjectName("muted")
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLORS['primary']};")
        
        sub_label = QLabel(subtitle)
        sub_label.setObjectName("muted")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(sub_label)
        
        # Store references for updating
        card.value_label = value_label
        card.title_label = title_label
        
        return card
    
    def update_scores(self, t_score: int, p_score: int, f_counts: tuple, c_size: int):
        """Update dashboard with new data."""
        # Calculate overall score
        overall = int((t_score + p_score) / 2)
        
        # Save to history
        blocked, total = f_counts
        self.score_history.add_entry(overall, t_score, p_score, blocked, total)
        
        # Update history chart
        history = self.score_history.get_history(7)
        trend = self.score_history.get_score_trend()
        self.history_chart.set_history(history, trend)
        
        self.score_label.setText(str(overall))
        self.score_label.setStyleSheet(f"""
            font-size: 64px;
            font-weight: bold;
            color: {get_score_color(overall)};
        """)
        
        # Update description
        if overall >= 80:
            self.score_desc.setText(tr("dashboard.excellent"))
        elif overall >= 60:
            self.score_desc.setText(tr("dashboard.good"))
        elif overall >= 40:
            self.score_desc.setText(tr("dashboard.needs_attention"))
        else:
            self.score_desc.setText(tr("dashboard.at_risk"))
        
        # Update stats
        self.stat_cards["telemetry"].value_label.setText(f"{t_score}%")
        self.stat_cards["permissions"].value_label.setText(f"{p_score}%")
        self.stat_cards["firewall"].value_label.setText(f"{blocked}/{total}")
        
        size_mb = c_size / (1024 * 1024)
        self.stat_cards["cleanup"].value_label.setText(f"{size_mb:.1f} MB")
    
    def refresh_translations(self):
        """Update all text with current language."""
        self.title.setText(tr("dashboard.title"))
        self.score_title.setText(tr("dashboard.privacy_score"))
        self.actions_title.setText(tr("dashboard.quick_actions"))
        self.protect_title.setText(tr("dashboard.max_protection"))
        self.protect_desc.setText(tr("dashboard.max_protection_desc"))
        self.protect_btn.setText(tr("dashboard.enable_all"))
        self.cleanup_title.setText(tr("dashboard.quick_cleanup"))
        self.cleanup_desc.setText(tr("dashboard.quick_cleanup_desc"))
        self.cleanup_btn.setText(tr("dashboard.clean_now"))
        
        # Update stat card titles
        self.stat_cards["telemetry"].title_label.setText(tr("nav.telemetry"))
        self.stat_cards["permissions"].title_label.setText(tr("nav.permissions"))
        self.stat_cards["firewall"].title_label.setText(tr("nav.firewall"))
        self.stat_cards["cleanup"].title_label.setText(tr("nav.cleanup"))
