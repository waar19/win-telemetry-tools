"""
Main Window
Application entry point and navigation.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon

from .styles import MAIN_STYLESHEET, COLORS
from .dashboard_panel import DashboardPanel
from .telemetry_panel import TelemetryPanel
from .permissions_panel import PermissionsPanel
from .cleanup_panel import CleanupPanel
from .firewall_panel import FirewallPanel
from .workers import DashboardDataWorker
from ..modules.telemetry_blocker import TelemetryBlocker
from ..modules.permissions_manager import PermissionsManager
from ..modules.firewall_manager import FirewallManager
from ..modules.tracking_cleaner import TrackingCleaner


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Privacy Dashboard")
        self.resize(1200, 800)
        self.setStyleSheet(MAIN_STYLESHEET)
        
        self._dashboard_worker = None
        self._init_managers()
        self._setup_ui()
    
    def _init_managers(self):
        self.telemetry = TelemetryBlocker()
        self.permissions = PermissionsManager()
        self.firewall = FirewallManager()
        self.cleaner = TrackingCleaner()
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"background-color: {COLORS['bg_card']}; border-right: 1px solid {COLORS['border']};")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(8)
        
        # App Title in Sidebar
        app_title = QLabel("Privacy Dashboard")
        app_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 24px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)
        
        # Navigation Buttons
        self.nav_btns = []
        
        self.btn_dashboard = self._create_nav_btn("Dashboard", "dashboard")
        self.btn_telemetry = self._create_nav_btn("Telemetry", "telemetry")
        self.btn_permissions = self._create_nav_btn("Permissions", "permissions")
        self.btn_cleanup = self._create_nav_btn("Cleanup", "cleanup")
        self.btn_firewall = self._create_nav_btn("Firewall", "firewall")
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_telemetry)
        sidebar_layout.addWidget(self.btn_permissions)
        sidebar_layout.addWidget(self.btn_cleanup)
        sidebar_layout.addWidget(self.btn_firewall)
        
        sidebar_layout.addStretch()
        
        # Version info
        version = QLabel("v1.0.0")
        version.setObjectName("muted")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version)
        
        main_layout.addWidget(sidebar)
        
        # Content Area
        self.stack = QStackedWidget()
        
        # Initialize panels (don't refresh data on init - lazy load)
        self.dashboard_panel = DashboardPanel()
        self.telemetry_panel = TelemetryPanel()
        self.permissions_panel = PermissionsPanel()
        self.cleanup_panel = CleanupPanel()
        self.firewall_panel = FirewallPanel()
        
        # Connect dashboard signals
        self.dashboard_panel.navigate_to.connect(self.navigate_to)
        self.dashboard_panel.action_requested.connect(self.handle_quick_action)
        
        # Add to stack
        self.stack.addWidget(self.dashboard_panel)
        self.stack.addWidget(self.telemetry_panel)
        self.stack.addWidget(self.permissions_panel)
        self.stack.addWidget(self.cleanup_panel)
        self.stack.addWidget(self.firewall_panel)
        
        main_layout.addWidget(self.stack)
        
        # Initialize with dashboard
        self.btn_dashboard.setChecked(True)
        self.update_dashboard_stats()
    
    def _create_nav_btn(self, text: str, page_id: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("sidebar")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.navigate_to(page_id))
        self.nav_btns.append(btn)
        return btn
    
    def navigate_to(self, page_id: str):
        # Update buttons state
        mapping = {
            "dashboard": (self.btn_dashboard, 0),
            "telemetry": (self.btn_telemetry, 1),
            "permissions": (self.btn_permissions, 2),
            "cleanup": (self.btn_cleanup, 3),
            "firewall": (self.btn_firewall, 4)
        }
        
        if page_id in mapping:
            btn, index = mapping[page_id]
            
            # Uncheck all others
            for b in self.nav_btns:
                b.setChecked(False)
            btn.setChecked(True)
            
            # Switch panel FIRST (instant UI response)
            self.stack.setCurrentIndex(index)
            
            # THEN refresh data in background
            if index == 0:
                self.update_dashboard_stats()
            elif index == 1:
                self.telemetry_panel.refresh_data()
            elif index == 2:
                self.permissions_panel.refresh_data()
            elif index == 3:
                self.cleanup_panel.refresh_data()
            elif index == 4:
                self.firewall_panel.refresh_data()
    
    def update_dashboard_stats(self):
        """Update stats on the dashboard panel in background."""
        self._dashboard_worker = DashboardDataWorker(
            self.telemetry, self.permissions, self.firewall, self.cleaner
        )
        self._dashboard_worker.finished.connect(self._on_dashboard_stats_loaded)
        self._dashboard_worker.start()
    
    @pyqtSlot(int, int, tuple, int)
    def _on_dashboard_stats_loaded(self, t_score: int, p_score: int, f_counts: tuple, c_size: int):
        """Handle loaded dashboard stats."""
        self.dashboard_panel.update_scores(t_score, p_score, f_counts, c_size)
    
    def handle_quick_action(self, action_id: str):
        """Execute quick actions from dashboard."""
        if action_id == "cleanup_all":
            self.navigate_to("cleanup")
            self.cleanup_panel.start_cleanup()
        elif action_id == "protect_all":
            # Execute protection sequence
            self.telemetry.block_all_telemetry()
            self.permissions.disable_all_permissions()
            self.firewall.block_all_telemetry()
            
            # Refresh UI
            self.update_dashboard_stats()
