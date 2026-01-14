"""
Firewall Panel
UI for managing firewall rules to block telemetry endpoints.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QCheckBox, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSlot

from .styles import COLORS
from .workers import FirewallDataWorker
from ..modules.firewall_manager import FirewallManager, FirewallRule
from ..i18n import tr


class FirewallPanel(QWidget):
    """Panel for managing firewall blocking rules."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = FirewallManager()
        self._worker = None
        self._is_loading = False
        self._has_admin = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_block = QVBoxLayout()
        self.title = QLabel(tr("firewall.title"))
        self.title.setObjectName("sectionTitle")
        self.subtitle = QLabel(tr("firewall.subtitle"))
        self.subtitle.setObjectName("subtitle")
        title_block.addWidget(self.title)
        title_block.addWidget(self.subtitle)
        
        header_layout.addLayout(title_block)
        header_layout.addStretch()
        
        # Actions
        self.block_btn = QPushButton(tr("firewall.block_all"))
        self.block_btn.clicked.connect(self.block_all)
        
        self.unblock_btn = QPushButton(tr("firewall.unblock_all"))
        self.unblock_btn.setObjectName("secondary")
        self.unblock_btn.clicked.connect(self.unblock_all)
        
        header_layout.addWidget(self.unblock_btn)
        header_layout.addWidget(self.block_btn)
        
        layout.addLayout(header_layout)
        
        # Admin Warning placeholder (will be shown if needed)
        self.warn_frame = QFrame()
        self.warn_frame.setObjectName("card")
        self.warn_frame.setStyleSheet(f"border: 1px solid {COLORS['warning']};")
        warn_layout = QHBoxLayout(self.warn_frame)
        warn_icon = QLabel("⚠️")
        self.warn_text = QLabel(tr("firewall.admin_warning"))
        warn_layout.addWidget(warn_icon)
        warn_layout.addWidget(self.warn_text)
        warn_layout.addStretch()
        self.warn_frame.setVisible(False)
        layout.addWidget(self.warn_frame)
        
        # Loading indicator
        self.loading_label = QLabel(tr("common.loading"))
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setObjectName("muted")
        self.loading_label.setVisible(False)
        layout.addWidget(self.loading_label)
        
        # Rules Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            tr("firewall.endpoint"), 
            tr("firewall.description"), 
            tr("firewall.status")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().resizeSection(2, 100)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        layout.addWidget(self.table)
   
    def refresh_data(self):
        """Reload firewall rules status in background."""
        if self._is_loading:
            return
        
        # Check admin rights once (cached after first check)
        if self._has_admin is None:
            self._has_admin = self.manager.check_admin_rights()
            if not self._has_admin:
                self.warn_frame.setVisible(True)
                self.block_btn.setEnabled(False)
                self.unblock_btn.setEnabled(False)
        
        self._is_loading = True
        self.loading_label.setVisible(True)
        
        self._worker = FirewallDataWorker(self.manager)
        self._worker.finished.connect(self._on_data_loaded)
        self._worker.start()
    
    @pyqtSlot(list)
    def _on_data_loaded(self, rules: list):
        """Handle loaded data."""
        self._is_loading = False
        self.loading_label.setVisible(False)
        
        self.table.setRowCount(len(rules))
        
        for i, rule in enumerate(rules):
            # Endpoint
            ep_item = QTableWidgetItem(rule.name)
            self.table.setItem(i, 0, ep_item)
            
            # Description
            desc_item = QTableWidgetItem(rule.description)
            self.table.setItem(i, 1, desc_item)
            
            # Status
            status_text = tr("firewall.blocked") if rule.is_active else tr("firewall.allowed")
            status_widget = QLabel(status_text)
            status_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_widget.setStyleSheet(
                f"color: {COLORS['success'] if rule.is_active else COLORS['danger']}; font-weight: bold;"
            )
            self.table.setCellWidget(i, 2, status_widget)
    
    @pyqtSlot()
    def block_all(self):
        success, msg = self.manager.block_all_telemetry()
        if success:
            QMessageBox.information(self, tr("common.success"), msg)
        else:
            QMessageBox.warning(self, tr("common.warning"), msg)
        self.refresh_data()
    
    @pyqtSlot()
    def unblock_all(self):
        success, msg = self.manager.unblock_all_telemetry()
        if success:
            QMessageBox.information(self, tr("common.success"), msg)
        else:
            QMessageBox.warning(self, tr("common.warning"), msg)
        self.refresh_data()
    
    def refresh_translations(self):
        """Update all text with current language."""
        self.title.setText(tr("firewall.title"))
        self.subtitle.setText(tr("firewall.subtitle"))
        self.block_btn.setText(tr("firewall.block_all"))
        self.unblock_btn.setText(tr("firewall.unblock_all"))
        self.warn_text.setText(tr("firewall.admin_warning"))
        self.loading_label.setText(tr("common.loading"))
        
        # Update table headers
        self.table.setHorizontalHeaderLabels([
            tr("firewall.endpoint"), 
            tr("firewall.description"), 
            tr("firewall.status")
        ])
