"""
Permissions Panel
UI for managing app permissions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QCheckBox, QPushButton,
    QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSlot

from .styles import COLORS
from ..modules.permissions_manager import PermissionsManager, PermissionType


class AppPermissionWidget(QFrame):
    """Widget for a single app permission."""
    
    def __init__(self, app_name: str, is_allowed: bool, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMaximumHeight(80)
        
        layout = QHBoxLayout(self)
        
        name_label = QLabel(app_name)
        name_label.setStyleSheet("font-weight: bold;")
        
        self.status_label = QLabel("Allowed" if is_allowed else "Denied")
        self.status_label.setStyleSheet(f"color: {COLORS['danger'] if is_allowed else COLORS['success']};")
        
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(self.status_label)


class PermissionsPanel(QWidget):
    """Panel for managing app permissions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = PermissionsManager()
        self.current_type = PermissionType.CAMERA
        self._setup_ui()
        self.refresh_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_block = QVBoxLayout()
        title = QLabel("App Permissions")
        title.setObjectName("sectionTitle")
        self.subtitle = QLabel("Manage access to Camera, Microphone, and more")
        self.subtitle.setObjectName("subtitle")
        title_block.addWidget(title)
        title_block.addWidget(self.subtitle)
        
        header_layout.addLayout(title_block)
        header_layout.addStretch()
        
        # Permission selector
        self.type_combo = QComboBox()
        for p_type in self.manager.MAIN_PERMISSIONS:
            name, _ = self.manager.PERMISSION_DISPLAY_NAMES[p_type]
            self.type_combo.addItem(name, p_type)
        
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        header_layout.addWidget(QLabel("Permission Type:"))
        header_layout.addWidget(self.type_combo)
        
        layout.addLayout(header_layout)
        
        # Global Toggle
        global_card = QFrame()
        global_card.setObjectName("card")
        global_layout = QHBoxLayout(global_card)
        
        global_info = QVBoxLayout()
        self.global_label = QLabel("Global Setting")
        self.global_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.global_desc = QLabel("Allow apps to access this resource")
        self.global_desc.setObjectName("muted")
        global_info.addWidget(self.global_label)
        global_info.addWidget(self.global_desc)
        
        self.global_toggle = QCheckBox()
        self.global_toggle.setObjectName("toggle")
        self.global_toggle.toggled.connect(self.on_global_toggle)
        
        global_layout.addLayout(global_info)
        global_layout.addStretch()
        global_layout.addWidget(self.global_toggle)
        
        layout.addWidget(global_card)
        
        # Apps List
        list_label = QLabel("Apps with Access")
        list_label.setStyleSheet("font-weight: bold; margin-top: 16px;")
        layout.addWidget(list_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(12)
        self.content_layout.addStretch()
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
    
    def on_type_changed(self, index):
        self.current_type = self.type_combo.currentData()
        self.refresh_data()
    
    def on_global_toggle(self, checked):
        success, msg = self.manager.set_permission_global_state(self.current_type, checked)
        if not success:
            QMessageBox.warning(self, "Error", dict(msg))
            # Revert toggle if failed
            self.global_toggle.blockSignals(True)
            self.global_toggle.setChecked(not checked)
            self.global_toggle.blockSignals(False)
        else:
            self.refresh_data()
    
    def refresh_data(self):
        """Reload permissions data."""
        status = self.manager.get_permission_status(self.current_type)
        if not status:
            return
            
        # Update global toggle
        self.global_toggle.blockSignals(True)
        self.global_toggle.setChecked(status.is_enabled)
        self.global_toggle.blockSignals(False)
        
        self.subtitle.setText(status.description)
        
        # Clear existing items
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Load apps
        apps = self.manager.get_apps_for_permission(self.current_type)
        
        if not apps:
            no_apps = QLabel("No apps found with this permission")
            no_apps.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_apps.setObjectName("muted")
            self.content_layout.insertWidget(0, no_apps)
        else:
            for app in apps:
                widget = AppPermissionWidget(app.app_name, app.is_allowed)
                self.content_layout.insertWidget(self.content_layout.count() - 1, widget)
