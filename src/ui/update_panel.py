"""
Update Control Panel
UI for managing Windows Update settings.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QMessageBox, QRadioButton,
    QButtonGroup
)
from PyQt6.QtCore import Qt

from .styles import COLORS
from ..modules.update_manager import UpdateManager
from ..i18n import tr


class UpdatePanel(QWidget):
    """Panel for Windows Update control."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = UpdateManager()
        self._setup_ui()
        self.refresh_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        self.title = QLabel("Windows Updates") # Todo: i18n
        self.title.setObjectName("sectionTitle")
        self.subtitle = QLabel("Control how and when your system updates")
        self.subtitle.setObjectName("subtitle")
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        
        # Current Status
        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QVBoxLayout(status_card)
        
        self.status_label = QLabel("Current Status: Unknown")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.desc_label = QLabel("Loading settings...")
        self.desc_label.setObjectName("muted")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.desc_label)
        layout.addWidget(status_card)
        
        # Controls
        controls_card = QFrame()
        controls_card.setObjectName("card")
        controls_layout = QVBoxLayout(controls_card)
        
        title = QLabel("Update Policy")
        title.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        controls_layout.addWidget(title)
        
        self.group = QButtonGroup()
        
        self.rb_default = QRadioButton("Default (Windows Managed)")
        self.rb_notify = QRadioButton("Notify before download (Prevent auto-download)")
        self.rb_disable = QRadioButton("Disable Automatic Updates")
        
        self.group.addButton(self.rb_default, 0)
        self.group.addButton(self.rb_notify, 1)
        self.group.addButton(self.rb_disable, 2)
        
        controls_layout.addWidget(self.rb_default)
        controls_layout.addWidget(self.rb_notify)
        controls_layout.addWidget(self.rb_disable)
        
        self.btn_apply = QPushButton("Apply Settings")
        self.btn_apply.clicked.connect(self.apply_settings)
        controls_layout.addWidget(self.btn_apply)
        
        layout.addWidget(controls_card)
        layout.addStretch()
    
    def refresh_data(self):
        """Load current settings."""
        status = self.manager.get_status()
        
        self.group.blockSignals(True)
        if status["no_auto_update"]:
            self.rb_disable.setChecked(True)
            self.status_label.setText("Current Status: Disabled")
            self.status_label.setStyleSheet(f"color: {COLORS['danger']}; font-weight: bold; font-size: 16px;")
            self.desc_label.setText("Automatic updates are completely disabled.")
        elif status["au_options"] == 2:
            self.rb_notify.setChecked(True)
            self.status_label.setText("Current Status: Notify Only")
            self.status_label.setStyleSheet(f"color: {COLORS['warning']}; font-weight: bold; font-size: 16px;")
            self.desc_label.setText("You will be notified when updates are available, but they won't download automatically.")
        else:
            self.rb_default.setChecked(True)
            self.status_label.setText("Current Status: Default")
            self.status_label.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold; font-size: 16px;")
            self.desc_label.setText("Windows manages updates automatically.")
        self.group.blockSignals(False)
    
    def apply_settings(self):
        """Apply selected policy."""
        checked_id = self.group.checkedId()
        success = False
        msg = ""
        
        if checked_id == 0:
            success, msg = self.manager.restore_defaults()
        elif checked_id == 1:
            success, msg = self.manager.set_notify_only()
        elif checked_id == 2:
            success, msg = self.manager.disable_auto_updates()
            
        if success:
            QMessageBox.information(self, "Success", msg)
            self.refresh_data()
        else:
            QMessageBox.warning(self, "Error", msg)
            
    def refresh_translations(self):
        pass
