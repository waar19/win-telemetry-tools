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
        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        wrapper_layout.addWidget(scroll)
        
        content = QWidget()
        scroll.setWidget(content)
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        self.title = QLabel(tr("updates.title"))
        self.title.setObjectName("sectionTitle")
        self.subtitle = QLabel(tr("updates.subtitle"))
        self.subtitle.setObjectName("subtitle")
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        
        # Current Status
        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QVBoxLayout(status_card)
        
        self.status_label = QLabel(f"{tr('updates.status')} ...")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.desc_label = QLabel(tr("common.loading"))
        self.desc_label.setObjectName("muted")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.desc_label)
        layout.addWidget(status_card)
        
        # Controls
        controls_card = QFrame()
        controls_card.setObjectName("card")
        controls_layout = QVBoxLayout(controls_card)
        
        self.policy_title = QLabel(tr("updates.policy"))
        self.policy_title.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        controls_layout.addWidget(self.policy_title)
        
        self.group = QButtonGroup()
        
        self.rb_default = QRadioButton(tr("updates.default"))
        self.rb_notify = QRadioButton(tr("updates.notify"))
        self.rb_disable = QRadioButton(tr("updates.disable"))
        
        self.group.addButton(self.rb_default, 0)
        self.group.addButton(self.rb_notify, 1)
        self.group.addButton(self.rb_disable, 2)
        
        controls_layout.addWidget(self.rb_default)
        controls_layout.addWidget(self.rb_notify)
        controls_layout.addWidget(self.rb_disable)
        
        self.btn_apply = QPushButton(tr("updates.apply"))
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
            self._update_status_labels(2)
        elif status["au_options"] == 2:
            self.rb_notify.setChecked(True)
            self._update_status_labels(1)
        else:
            self.rb_default.setChecked(True)
            self._update_status_labels(0)
        self.group.blockSignals(False)
    
    def _update_status_labels(self, mode):
        """Update status labels based on mode 0=default, 1=notify, 2=disable."""
        if mode == 2:
            self.status_label.setText(f"{tr('updates.status')} {tr('updates.disable')}")
            self.status_label.setStyleSheet(f"color: {COLORS['danger']}; font-weight: bold; font-size: 16px;")
            self.desc_label.setText(tr("updates.desc_disable"))
        elif mode == 1:
            self.status_label.setText(f"{tr('updates.status')} {tr('updates.notify')}")
            self.status_label.setStyleSheet(f"color: {COLORS['warning']}; font-weight: bold; font-size: 16px;")
            self.desc_label.setText(tr("updates.desc_notify"))
        else:
            self.status_label.setText(f"{tr('updates.status')} {tr('updates.default')}")
            self.status_label.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold; font-size: 16px;")
            self.desc_label.setText(tr("updates.desc_default"))
            
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
            QMessageBox.information(self, tr("common.success"), msg)
            self.refresh_data()
        else:
            QMessageBox.warning(self, tr("common.error"), msg)
            
    def refresh_translations(self):
        self.title.setText(tr("updates.title"))
        self.subtitle.setText(tr("updates.subtitle"))
        self.policy_title.setText(tr("updates.policy"))
        self.rb_default.setText(tr("updates.default"))
        self.rb_notify.setText(tr("updates.notify"))
        self.rb_disable.setText(tr("updates.disable"))
        self.btn_apply.setText(tr("updates.apply"))
        
        # Refresh status text using current selection
        self.refresh_data()
