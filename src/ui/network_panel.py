"""
Network Panel
Real-time view of active network connections.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot

from .styles import COLORS
from ..modules.network_monitor import NetworkMonitor
from ..i18n import tr


class NetworkPanel(QWidget):
    """Panel for monitoring network connections."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.monitor = NetworkMonitor()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.is_monitoring = False
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_block = QVBoxLayout()
        self.title = QLabel(tr("network.title"))
        self.title.setObjectName("sectionTitle")
        self.subtitle = QLabel(tr("network.subtitle"))
        self.subtitle.setObjectName("subtitle")
        title_block.addWidget(self.title)
        title_block.addWidget(self.subtitle)
        
        header_layout.addLayout(title_block)
        header_layout.addStretch()
        
        # Control Buttons
        self.btn_toggle = QPushButton(tr("network.start"))
        self.btn_toggle.clicked.connect(self.toggle_monitoring)
        self.btn_toggle.setCheckable(True)
        
        header_layout.addWidget(self.btn_toggle)
        
        layout.addLayout(header_layout)
        
        # Connections Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self._update_table_headers()
        
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Status Bar
        self.status_label = QLabel(tr("network.stopped"))
        self.status_label.setObjectName("muted")
        layout.addWidget(self.status_label)
    
    def _update_table_headers(self):
        self.table.setHorizontalHeaderLabels([
            tr("network.process"), 
            tr("network.remote_addr"), 
            tr("network.hostname"), 
            tr("network.status"), 
            tr("network.type")
        ])
    
    def toggle_monitoring(self, checked):
        state = self.btn_toggle.isChecked()
        if state:
            self.btn_toggle.setText(tr("network.stop"))
            self.status_label.setText(tr("network.active"))
            self.start_monitoring()
        else:
            self.btn_toggle.setText(tr("network.start"))
            self.status_label.setText(tr("network.stopped"))
            self.stop_monitoring()
    
    def start_monitoring(self):
        self.is_monitoring = True
        self.timer.start(2000)  # Update every 2 seconds
        self.refresh_data()
    
    def stop_monitoring(self):
        self.is_monitoring = False
        self.timer.stop()
    
    def refresh_data(self):
        """Update table with active connections."""
        if not self.is_monitoring:
            return
            
        connections = self.monitor.get_connections()
        
        self.table.setRowCount(len(connections))
        self.status_label.setText(f"{tr('network.active_connections')} {len(connections)}")
        
        for i, conn in enumerate(connections):
            # Process
            name_item = QTableWidgetItem(f"{conn.process_name} ({conn.pid})")
            self.table.setItem(i, 0, name_item)
            
            # Remote IP
            self.table.setItem(i, 1, QTableWidgetItem(conn.remote_address))
            
            # Hostname
            host_item = QTableWidgetItem(conn.hostname or "Resolving...")
            if conn.is_telemetry:
                host_item.setForeground(QFrame(color=COLORS["danger"]).palette().windowText())
            self.table.setItem(i, 2, host_item)
            
            # Status
            self.table.setItem(i, 3, QTableWidgetItem(conn.status))
            
            # Type
            type_str = "Telemetry" if conn.is_telemetry else "Normal"
            type_item = QTableWidgetItem(type_str)
            if conn.is_telemetry:
                type_item.setBackground(QFrame(color=COLORS["warning"]).palette().window())
                type_item.setForeground(Qt.GlobalColor.black)
            self.table.setItem(i, 4, type_item)
    
    def refresh_translations(self):
        self.title.setText(tr("network.title"))
        self.subtitle.setText(tr("network.subtitle"))
        
        if self.btn_toggle.isChecked():
            self.btn_toggle.setText(tr("network.stop"))
            if not self.is_monitoring: # Should ideally be synced logic
                 pass
        else:
            self.btn_toggle.setText(tr("network.start"))
            self.status_label.setText(tr("network.stopped"))

        self._update_table_headers()
