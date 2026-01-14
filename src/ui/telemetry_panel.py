"""
Telemetry Panel
UI for managing Windows telemetry settings.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QCheckBox, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from .styles import COLORS
from ..modules.telemetry_blocker import TelemetryBlocker, TelemetryItem


class TelemetryItemWidget(QFrame):
    """Widget representing a single telemetry setting."""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, item: TelemetryItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.setObjectName("card")
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Info
        info_layout = QVBoxLayout()
        name_label = QLabel(self.item.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        
        desc_label = QLabel(self.item.description)
        desc_label.setObjectName("muted")
        desc_label.setWordWrap(True)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        
        # Toggle switch
        self.toggle = QCheckBox()
        self.toggle.setObjectName("toggle")
        self.toggle.setChecked(self.item.is_blocked)
        self.toggle.toggled.connect(self.toggled.emit)
        
        layout.addLayout(info_layout, stretch=1)
        layout.addWidget(self.toggle)


class TelemetryPanel(QWidget):
    """Panel for managing telemetry settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocker = TelemetryBlocker()
        self._setup_ui()
        self.refresh_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_block = QVBoxLayout()
        title = QLabel("Telemetry & Tracking")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("Manage Windows data collection and scheduled tasks")
        subtitle.setObjectName("subtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        
        header_layout.addLayout(title_block)
        header_layout.addStretch()
        
        # Actions
        self.block_all_btn = QPushButton("Block All")
        self.block_all_btn.clicked.connect(self.block_all)
        
        self.restore_btn = QPushButton("Restore Defaults")
        self.restore_btn.setObjectName("secondary")
        self.restore_btn.clicked.connect(self.restore_defaults)
        
        header_layout.addWidget(self.restore_btn)
        header_layout.addWidget(self.block_all_btn)
        
        layout.addLayout(header_layout)
        
        # Content Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(12)
        self.content_layout.addStretch()
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
    
    def refresh_data(self):
        """Reload telemetry status."""
        # Clear existing items
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Load items
        items = self.blocker.get_telemetry_status()
        
        # Group by category
        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        # Add to layout
        for category, cat_items in categories.items():
            cat_label = QLabel(category)
            cat_label.setStyleSheet("font-weight: bold; margin-top: 16px; margin-bottom: 8px;")
            self.content_layout.insertWidget(self.content_layout.count() - 1, cat_label)
            
            for item in cat_items:
                widget = TelemetryItemWidget(item)
                # Note: Individual toggling logic would go here
                # For now we rely on Block All / Restore
                self.content_layout.insertWidget(self.content_layout.count() - 1, widget)
    
    @pyqtSlot()
    def block_all(self):
        success, msg = self.blocker.block_all_telemetry()
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.warning(self, "Warning", f"Some items failed:\n{msg}")
        self.refresh_data()
    
    @pyqtSlot()
    def restore_defaults(self):
        success, msg = self.blocker.unblock_all_telemetry()
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.warning(self, "Warning", f"Some items failed:\n{msg}")
        self.refresh_data()
