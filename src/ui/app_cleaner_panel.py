"""
App Cleaner Panel
UI for removing Windows built-in apps (bloatware).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QMessageBox, QProgressDialog,
    QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from .styles import COLORS
from ..i18n import tr
from ..modules.app_manager import AppManager


class AppScanWorker(QThread):
    """Async worker to scan installed apps."""
    finished = pyqtSignal(list)
    
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
    def run(self):
        apps = self.manager.get_installed_apps()
        self.finished.emit(apps)


class AppRemoveWorker(QThread):
    """Async worker to remove selected apps."""
    progress = pyqtSignal(str) # Current app being removed
    finished = pyqtSignal(int, int) # removed_count, failed_count
    
    def __init__(self, manager, apps_to_remove):
        super().__init__()
        self.manager = manager
        self.apps_to_remove = apps_to_remove # List of package IDs
        
    def run(self):
        removed = 0
        failed = 0
        for app_id in self.apps_to_remove:
            self.progress.emit(app_id)
            if self.manager.remove_app(app_id):
                removed += 1
            else:
                failed += 1
        self.finished.emit(removed, failed)


class AppCleanerPanel(QWidget):
    """Panel for managing Windows Apps."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = AppManager()
        self._apps_data = [] # Store raw data
        self._setup_ui()
        
    def _setup_ui(self):
        # Wrapper for scroll/styling consistency
        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24) # Reduced margins
        layout.setSpacing(16)
        wrapper_layout.addLayout(layout)
        
        # Header
        self.title = QLabel("App Cleaner") 
        self.title.setObjectName("sectionTitle")
        self.subtitle = QLabel("Remove unwanted pre-installed Windows applications")
        self.subtitle.setObjectName("subtitle")
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.status_label = QLabel("Click Scan to list apps...")
        self.status_label.setStyleSheet("font-weight: bold;")
        
        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search apps...")
        self.search_input.setFixedWidth(250)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                color: {COLORS['text_primary']};
                background-color: {COLORS['bg_card']};
            }}
        """)
        self.search_input.textChanged.connect(self.filter_apps)
        
        self.btn_scan = QPushButton("Scan Apps")
        self.btn_scan.clicked.connect(self.start_scan)
        
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_remove.setObjectName("danger")
        self.btn_remove.setEnabled(False)
        self.btn_remove.clicked.connect(self.remove_selected)
        
        toolbar.addWidget(self.status_label)
        toolbar.addStretch()
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.btn_scan)
        toolbar.addWidget(self.btn_remove)
        
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Select", "App Name", "Publisher", "Type"])
        
        # Optimize Columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed) # Checkbox
        self.table.setColumnWidth(0, 50)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Name (Most Important)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Publisher
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Type
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table)
        
        layout.addStretch()
        
        # Initial scan
        # self.start_scan() # Maybe wait for user? Or auto-scan. Auto-scan is better UX.
        
    def start_scan(self):
        self.btn_scan.setEnabled(False)
        self.status_label.setText("Scanning installed applications...")
        self.table.setRowCount(0)
        
        self.worker = AppScanWorker(self.manager)
        self.worker.finished.connect(self._on_scan_finished)
        self.worker.start()
        
    def _on_scan_finished(self, apps):
        self._apps_data = apps
        self.table.blockSignals(True) # Prevent itemChanged during setup
        self.table.setRowCount(len(apps))
        
        for row, app in enumerate(apps):
            # Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            self.table.setItem(row, 0, chk_item)
            
            # Name
            name_item = QTableWidgetItem(app["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, app["id"]) # Store ID being removed
            self.table.setItem(row, 1, name_item)
            
            # Publisher
            pub_raw = app["publisher"]
            # Shorten publisher "CN=Microsoft Corporation, ..."
            if "CN=" in pub_raw:
                pub_raw = pub_raw.split("CN=")[1].split(",")[0]
            self.table.setItem(row, 2, QTableWidgetItem(pub_raw))
            
            # Type (Bloatware vs User)
            if app.get("is_critical", False):
                type_str = "CRITICAL SYSTEM APP"
                type_item = QTableWidgetItem(type_str)
                type_item.setForeground(Qt.GlobalColor.red)
                type_item.setData(Qt.ItemDataRole.UserRole, "critical") # Mark as critical
                
                # Disable checkbox for critical apps by default
                chk_item.setFlags(Qt.ItemFlag.NoItemFlags) # Make non-interactable or just disabled
                chk_item.setFlags(Qt.ItemFlag.ItemIsEnabled) # Just enabled but not checkable? No, usually ItemIsUserCheckable is needed.
                # Let's make it disabled completely
                chk_item.setFlags(Qt.ItemFlag.NoItemFlags)
                
            elif app["is_bloatware"]:
                type_str = "Recommended Removal"
                type_item = QTableWidgetItem(type_str)
                type_item.setForeground(Qt.GlobalColor.darkYellow) # Yellow for caution/bloat
            else:
                type_str = "System/User App"
                type_item = QTableWidgetItem(type_str)
                type_item.setForeground(Qt.GlobalColor.darkGreen)
            
            self.table.setItem(row, 3, type_item)
            
        self.table.blockSignals(False) # Re-enable signals
        self.btn_scan.setEnabled(True)
        self.status_label.setText(f"Found {len(apps)} apps.")
        
    def _on_item_changed(self, item):
        # Enable remove button if any checked
        if item.column() == 0:
            checked = self._get_checked_apps()
            self.btn_remove.setEnabled(len(checked) > 0)
            self.btn_remove.setText(f"Remove Selected ({len(checked)})")

    def _get_checked_apps(self):
        selected_ids = []
        for row in range(self.table.rowCount()):
            chk = self.table.item(row, 0)
            if chk and chk.checkState() == Qt.CheckState.Checked:
                # Retrieve ID from column 1 UserRole
                name_item = self.table.item(row, 1)
                if name_item:
                    app_id = name_item.data(Qt.ItemDataRole.UserRole)
                    selected_ids.append(app_id)
        return selected_ids

    def remove_selected(self):
        apps = self._get_checked_apps()
        if not apps:
            return
            
        confirm = QMessageBox.warning(
            self, 
            "Confirm Removal",
            f"Are you sure you want to remove {len(apps)} applications?\nThis action cannot be easily undone without reinstalling.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self._start_removal_process(apps)
            
    def _start_removal_process(self, apps):
        # Progress dialog
        self.progress = QProgressDialog("Removing apps...", "Cancel", 0, len(apps), self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()
        
        self.remove_worker = AppRemoveWorker(self.manager, apps)
        self.remove_worker.progress.connect(self._on_removal_progress)
        self.remove_worker.finished.connect(self._on_removal_finished)
        self.remove_worker.start()
        
    def _on_removal_progress(self, app_id):
        val = self.progress.value()
        self.progress.setValue(val + 1)
        self.progress.setLabelText(f"Removing {app_id[:20]}...")
        
    def _on_removal_finished(self, removed, failed):
        self.progress.close()
        msg = f"Removed {removed} apps."
        if failed > 0:
            msg += f"\nFailed to remove {failed} apps."
        
        QMessageBox.information(self, "Cleanup Complete", msg)
        self.start_scan() # Refresh list
    
    def filter_apps(self, text):
        """Filter table rows based on search text."""
        text = text.lower()
        for row in range(self.table.rowCount()):
            # Look in Name (col 1) and Publisher (col 2)
            name_item = self.table.item(row, 1)
            pub_item = self.table.item(row, 2)
            
            show_row = False
            if name_item and text in name_item.text().lower():
                show_row = True
            elif pub_item and text in pub_item.text().lower():
                show_row = True
                
            self.table.setRowHidden(row, not show_row)
            
    def refresh_translations(self):
        self.title.setText(tr("apps.title"))
        self.subtitle.setText(tr("apps.subtitle"))
        self.btn_scan.setText(tr("apps.scan"))
        # Update search placeholder if we had a key, but hardcoded for now is fine or add key
        # self.search_input.setPlaceholderText(tr("apps.search"))
