"""
Dashboard Panel
Main panel with privacy score and stats.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from .styles import COLORS, get_score_color
from ..i18n import tr


class DashboardPanel(QWidget):
    """Main dashboard with privacy overview."""
    
    navigate_to = pyqtSignal(str)
    action_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        layout.addStretch()
    
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
        
        blocked, total = f_counts
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
