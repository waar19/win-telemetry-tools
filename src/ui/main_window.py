"""
Main Window
Application entry point and navigation.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot

from .styles import MAIN_STYLESHEET, COLORS
from .dashboard_panel import DashboardPanel
from .telemetry_panel import TelemetryPanel
from .permissions_panel import PermissionsPanel
from .cleanup_panel import CleanupPanel
from .firewall_panel import FirewallPanel
from .network_panel import NetworkPanel
from .update_panel import UpdatePanel
from .settings_panel import SettingsPanel
from .workers import DashboardDataWorker
from ..modules.telemetry_blocker import TelemetryBlocker
from ..modules.permissions_manager import PermissionsManager
from ..modules.firewall_manager import FirewallManager
from ..modules.tracking_cleaner import TrackingCleaner
from ..i18n import tr


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app.title"))
        self.resize(1080, 720) # Optimized for 1366x768 screens
        self.setMinimumSize(960, 600)
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
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet(f"background-color: {COLORS['bg_card']}; border-right: 1px solid {COLORS['border']};")
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(8)
        
        # App Title in Sidebar
        self.app_title = QLabel(tr("app.title"))
        self.app_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 24px;")
        self.app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.app_title)
        
        # Navigation Buttons
        self.nav_btns = []
        
        self.btn_dashboard = self._create_nav_btn(tr("nav.dashboard"), "dashboard")
        self.btn_telemetry = self._create_nav_btn(tr("nav.telemetry"), "telemetry")
        self.btn_permissions = self._create_nav_btn(tr("nav.permissions"), "permissions")
        self.btn_cleanup = self._create_nav_btn(tr("nav.cleanup"), "cleanup")
        self.btn_firewall = self._create_nav_btn(tr("nav.firewall"), "firewall")
        self.btn_network = self._create_nav_btn(tr("nav.network"), "network")
        self.btn_updates = self._create_nav_btn(tr("nav.updates"), "updates")
        self.btn_settings = self._create_nav_btn(tr("nav.settings"), "settings")
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_telemetry)
        sidebar_layout.addWidget(self.btn_permissions)
        sidebar_layout.addWidget(self.btn_cleanup)
        sidebar_layout.addWidget(self.btn_firewall)
        sidebar_layout.addWidget(self.btn_network)
        sidebar_layout.addWidget(self.btn_updates)
        
        sidebar_layout.addStretch()
        
        sidebar_layout.addWidget(self.btn_settings)
        
        # Version info
        self.version_label = QLabel(tr("app.version"))
        self.version_label.setObjectName("muted")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.version_label)
        
        main_layout.addWidget(self.sidebar)
        
        # Content Area
        self.stack = QStackedWidget()
        
        # Initialize panels
        self.dashboard_panel = DashboardPanel()
        self.telemetry_panel = TelemetryPanel()
        self.permissions_panel = PermissionsPanel()
        self.cleanup_panel = CleanupPanel()
        self.firewall_panel = FirewallPanel()
        self.network_panel = NetworkPanel()
        self.update_panel = UpdatePanel()
        self.settings_panel = SettingsPanel()
        
        # Connect dashboard signals
        self.dashboard_panel.navigate_to.connect(self.navigate_to)
        self.dashboard_panel.action_requested.connect(self.handle_quick_action)
        
        # Connect settings language change
        self.settings_panel.language_changed.connect(self._on_language_changed)
        
        # Add to stack
        self.stack.addWidget(self.dashboard_panel)
        self.stack.addWidget(self.telemetry_panel)
        self.stack.addWidget(self.permissions_panel)
        self.stack.addWidget(self.cleanup_panel)
        self.stack.addWidget(self.firewall_panel)
        self.stack.addWidget(self.network_panel)
        self.stack.addWidget(self.update_panel)
        self.stack.addWidget(self.settings_panel)
        
        main_layout.addWidget(self.stack)
        
        # Initialize with dashboard
        self.btn_dashboard.setChecked(True)
        self.update_dashboard_stats()
    
    def _create_nav_btn(self, text: str, page_id: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("sidebar")
        btn.setCheckable(True)
        btn.setProperty("page_id", page_id)
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
            "firewall": (self.btn_firewall, 4),
            "network": (self.btn_network, 5),
            "updates": (self.btn_updates, 6),
            "settings": (self.btn_settings, 7)
        }
        
        if page_id in mapping:
            btn, index = mapping[page_id]
            
            # Uncheck all others
            for b in self.nav_btns:
                b.setChecked(False)
            btn.setChecked(True)
            
            # Switch panel FIRST
            self.stack.setCurrentIndex(index)
            
            # THEN refresh data
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
            elif index == 5:
                self.network_panel.start_monitoring()
            elif index == 6:
                self.update_panel.refresh_data()
            
            # Stop network scan when leaving the page
            if index != 5:
                self.network_panel.stop_monitoring()
    
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
    
    @pyqtSlot(str)
    def _on_language_changed(self, lang_code: str):
        """Handle language change from settings."""
        self._update_all_translations()
    
    def _update_all_translations(self):
        """Update all UI text with current language."""
        # Update window title
        self.setWindowTitle(tr("app.title"))
        
        # Update sidebar
        self.app_title.setText(tr("app.title"))
        self.btn_dashboard.setText(tr("nav.dashboard"))
        self.btn_telemetry.setText(tr("nav.telemetry"))
        self.btn_permissions.setText(tr("nav.permissions"))
        self.btn_cleanup.setText(tr("nav.cleanup"))
        self.btn_firewall.setText(tr("nav.firewall"))
        self.btn_network.setText(tr("nav.network"))
        self.btn_updates.setText(tr("nav.updates"))
        self.btn_settings.setText(tr("nav.settings"))
        
        # Update panels
        self.dashboard_panel.refresh_translations()
        self.telemetry_panel.refresh_translations()
        self.permissions_panel.refresh_translations()
        self.cleanup_panel.refresh_translations()
        self.firewall_panel.refresh_translations()
        self.network_panel.refresh_translations()
        self.update_panel.refresh_translations()
