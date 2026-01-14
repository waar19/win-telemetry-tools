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
from .workers import PermissionsDataWorker
from ..modules.permissions_manager import PermissionsManager, PermissionType
from ..i18n import tr


class AppPermissionWidget(QFrame):
    """Widget for a single app permission."""
    
    def __init__(self, app_name: str, is_allowed: bool, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMaximumHeight(80)
        
        layout = QHBoxLayout(self)
        
        name_label = QLabel(app_name)
        name_label.setStyleSheet("font-weight: bold;")
        
        status_text = tr("permissions.allowed") if is_allowed else tr("permissions.denied")
        self.status_label = QLabel(status_text)
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
        self._worker = None
        self._is_loading = False
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_block = QVBoxLayout()
        self.title = QLabel(tr("permissions.title"))
        self.title.setObjectName("sectionTitle")
        self.subtitle = QLabel(tr("permissions.subtitle"))
        self.subtitle.setObjectName("subtitle")
        title_block.addWidget(self.title)
        title_block.addWidget(self.subtitle)
        
        header_layout.addLayout(title_block)
        header_layout.addStretch()
        
        # Permission selector
        self.type_combo = QComboBox()
        for p_type in self.manager.MAIN_PERMISSIONS:
            name, _ = self.manager.PERMISSION_DISPLAY_NAMES[p_type]
            self.type_combo.addItem(name, p_type)
        
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.type_label = QLabel(tr("permissions.type_label"))
        header_layout.addWidget(self.type_label)
        header_layout.addWidget(self.type_combo)
        
        layout.addLayout(header_layout)
        
        # Global Toggle
        global_card = QFrame()
        global_card.setObjectName("card")
        global_layout = QHBoxLayout(global_card)
        
        global_info = QVBoxLayout()
        self.global_label = QLabel(tr("permissions.global_setting"))
        self.global_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.global_desc = QLabel(tr("permissions.global_desc"))
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
        
        # Loading indicator
        self.loading_label = QLabel(tr("common.loading"))
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setObjectName("muted")
        self.loading_label.setVisible(False)
        layout.addWidget(self.loading_label)
        
        # Apps List
        self.list_label = QLabel(tr("permissions.apps_with_access"))
        self.list_label.setStyleSheet("font-weight: bold; margin-top: 16px;")
        layout.addWidget(self.list_label)
        
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
            QMessageBox.warning(self, tr("common.error"), str(msg))
            # Revert toggle if failed
            self.global_toggle.blockSignals(True)
            self.global_toggle.setChecked(not checked)
            self.global_toggle.blockSignals(False)
        else:
            self.refresh_data()
    
    def refresh_data(self):
        """Reload permissions data in background."""
        if self._is_loading:
            return
        
        self._is_loading = True
        self.loading_label.setVisible(True)
        self.type_combo.setEnabled(False)
        self.global_toggle.setEnabled(False)
        
        self._worker = PermissionsDataWorker(self.manager, self.current_type)
        self._worker.finished.connect(self._on_data_loaded)
        self._worker.start()
    
    @pyqtSlot(object, list)
    def _on_data_loaded(self, status, apps: list):
        """Handle loaded data."""
        self._is_loading = False
        self.loading_label.setVisible(False)
        self.type_combo.setEnabled(True)
        self.global_toggle.setEnabled(True)
        
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
        
        if not apps:
            no_apps = QLabel(tr("permissions.no_apps"))
            no_apps.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_apps.setObjectName("muted")
            self.content_layout.insertWidget(0, no_apps)
        else:
            for app in apps:
                widget = AppPermissionWidget(app.app_name, app.is_allowed)
                self.content_layout.insertWidget(self.content_layout.count() - 1, widget)
    
    def refresh_translations(self):
        """Update all text with current language."""
        self.title.setText(tr("permissions.title"))
        self.subtitle.setText(tr("permissions.subtitle"))
        self.type_label.setText(tr("permissions.type_label"))
        self.global_label.setText(tr("permissions.global_setting"))
        self.global_desc.setText(tr("permissions.global_desc"))
        self.list_label.setText(tr("permissions.apps_with_access"))
        self.loading_label.setText(tr("common.loading"))
