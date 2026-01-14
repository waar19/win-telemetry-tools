"""
Cleanup Panel
UI for cleaning tracking data including System and Browsers.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QCheckBox, QPushButton,
    QMessageBox, QProgressBar, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal

from .styles import COLORS
from .workers import CleanupDataWorker
from ..modules.tracking_cleaner import TrackingCleaner, CleanupItem
from ..modules.browser_cleaner import BrowserCleaner, BrowserItem
from ..i18n import tr


class CleanWorker(QThread):
    """Worker thread for system cleanup operations."""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(bool, str, int)
    
    def __init__(self, cleaner: TrackingCleaner):
        super().__init__()
        self.cleaner = cleaner
    
    def run(self):
        success, msg, bytes_cleaned = self.cleaner.clean_all(self.progress.emit)
        self.finished.emit(success, msg, bytes_cleaned)


class BrowserCleanWorker(QThread):
    """Worker thread for browser cleanup."""
    finished = pyqtSignal(bool, str, int)
    
    def __init__(self, cleaner: BrowserCleaner, items: list):
        super().__init__()
        self.cleaner = cleaner
        self.items = items
    
    def run(self):
        success, msg, bytes_cleaned = self.cleaner.clean_items(self.items)
        self.finished.emit(success, msg, bytes_cleaned)


class BrowserItemWidget(QFrame):
    """Widget for a browser cleanup item."""
    def __init__(self, item: BrowserItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.setObjectName("card")
        
        layout = QHBoxLayout(self)
        
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(False) # Default unchecked for safety
        
        info_layout = QVBoxLayout()
        name_label = QLabel(item.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        desc_label = QLabel(item.description)
        desc_label.setObjectName("muted")
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        
        type_label = QLabel(item.browser)
        type_label.setStyleSheet(f"color: {COLORS['primary']}; font-weight: bold;")
        
        layout.addWidget(self.checkbox)
        layout.addLayout(info_layout, stretch=1)
        layout.addWidget(type_label)


class CleanupPanel(QWidget):
    """Panel for cleaning tracking data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cleaner = TrackingCleaner()
        self.browser_cleaner = BrowserCleaner()
        self._worker = None
        self._is_loading = False
        self._browser_widgets = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        self.title = QLabel(tr("cleanup.title"))
        self.title.setObjectName("sectionTitle")
        layout.addWidget(self.title)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # System Tab
        self.system_tab = QWidget()
        self._setup_system_tab()
        self.tabs.addTab(self.system_tab, "Windows System")
        
        # Browsers Tab
        self.browsers_tab = QWidget()
        self._setup_browsers_tab()
        self.tabs.addTab(self.browsers_tab, "Browsers")
        
        layout.addWidget(self.tabs)
        
        # Initialize
        self.refresh_browser_list()
    
    def _setup_system_tab(self):
        layout = QVBoxLayout(self.system_tab)
        layout.setContentsMargins(16, 24, 16, 16)
        
        # Header
        header = QHBoxLayout()
        subtitle = QLabel("Clean system history and tracking data")
        subtitle.setObjectName("subtitle")
        self.clean_btn = QPushButton(tr("cleanup.clean_all"))
        self.clean_btn.clicked.connect(self.start_cleanup)
        header.addWidget(subtitle)
        header.addStretch()
        header.addWidget(self.clean_btn)
        layout.addLayout(header)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)

        # List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(12)
        self.content_layout.addStretch()
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        self.loading_label = QLabel(tr("common.loading"))
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setVisible(False)
        layout.addWidget(self.loading_label)
    
    def _setup_browsers_tab(self):
        layout = QVBoxLayout(self.browsers_tab)
        layout.setContentsMargins(16, 24, 16, 16)
        
        # Header
        header = QHBoxLayout()
        subtitle = QLabel("Clean browsing data (Cache, Cookies, History)")
        subtitle.setObjectName("subtitle")
        self.clean_browser_btn = QPushButton("Clean Selected")
        self.clean_browser_btn.clicked.connect(self.start_browser_cleanup)
        header.addWidget(subtitle)
        header.addStretch()
        header.addWidget(self.clean_browser_btn)
        layout.addLayout(header)
        
        # List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.browser_content_widget = QWidget()
        self.browser_content_layout = QVBoxLayout(self.browser_content_widget)
        self.browser_content_layout.setSpacing(12)
        self.browser_content_layout.addStretch()
        scroll.setWidget(self.browser_content_widget)
        layout.addWidget(scroll)

    def refresh_data(self):
        """Reload system items status in background."""
        if self._is_loading:
            return
        
        self._is_loading = True
        self.loading_label.setVisible(True)
        self.clean_btn.setEnabled(False)
        
        self._worker = CleanupDataWorker(self.cleaner)
        self._worker.finished.connect(self._on_data_loaded)
        self._worker.start()
        
    def refresh_browser_list(self):
        """Load browser items."""
        # Clear existing
        while self.browser_content_layout.count() > 1:
            item = self.browser_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._browser_widgets = []
        
        items = self.browser_cleaner.get_cleanable_items()
        
        if not items:
            label = QLabel("No supported browsers found")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.browser_content_layout.insertWidget(0, label)
        else:
            for item in items:
                widget = BrowserItemWidget(item)
                self._browser_widgets.append(widget)
                self.browser_content_layout.insertWidget(self.browser_content_layout.count() - 1, widget)

    @pyqtSlot(list)
    def _on_data_loaded(self, items: list):
        """Handle loaded data."""
        self._is_loading = False
        self.loading_label.setVisible(False)
        self.clean_btn.setEnabled(True)
        
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for item in items:
            widget = self._create_item_widget(item)
            self.content_layout.insertWidget(self.content_layout.count() - 1, widget)
    
    def _create_item_widget(self, item: CleanupItem) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        layout = QHBoxLayout(frame)
        
        info_layout = QVBoxLayout()
        name_label = QLabel(item.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        desc_label = QLabel(item.description)
        desc_label.setObjectName("muted")
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        
        size_str = self.cleaner._format_size(item.size_bytes)
        size_label = QLabel(size_str)
        size_label.setStyleSheet("font-weight: bold; color: " + COLORS["primary"])
        
        layout.addLayout(info_layout, stretch=1)
        layout.addWidget(size_label)
        return frame
    
    @pyqtSlot()
    def start_cleanup(self):
        self.clean_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = CleanWorker(self.cleaner)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.cleanup_finished)
        self.worker.start()
    
    @pyqtSlot()
    def start_browser_cleanup(self):
        selected_items = [w.item for w in self._browser_widgets if w.checkbox.isChecked()]
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select at least one item to clean")
            return
            
        confirm = QMessageBox.question(
            self, "Confirm Cleanup", 
            "Selected browser data will be permanently deleted. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.clean_browser_btn.setEnabled(False)
        self.browser_worker = BrowserCleanWorker(self.browser_cleaner, selected_items)
        self.browser_worker.finished.connect(self.browser_cleanup_finished)
        self.browser_worker.start()

    @pyqtSlot(int, int, str)
    def update_progress(self, current, total, item_name):
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(f"{tr('cleanup.cleaning')} {item_name}")
    
    @pyqtSlot(bool, str, int)
    def cleanup_finished(self, success, msg, bytes_cleaned):
        self.clean_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        if success:
            cleaned_str = self.cleaner._format_size(bytes_cleaned)
            QMessageBox.information(self, tr("cleanup.complete"), 
                                  f"{tr('cleanup.complete_msg')}\n{tr('cleanup.freed')} {cleaned_str}")
        else:
            QMessageBox.warning(self, tr("common.warning"), msg)
        self.refresh_data()

    @pyqtSlot(bool, str, int)
    def browser_cleanup_finished(self, success, msg, bytes_cleaned):
        self.clean_browser_btn.setEnabled(True)
        if success:
            cleaned_str = self.cleaner._format_size(bytes_cleaned)
            QMessageBox.information(self, "Framework Cleanup", 
                                  f"Cleanup complete.\nFreed space: {cleaned_str}")
        else:
            QMessageBox.warning(self, "Error", f"Errors occurred:\n{msg}")
        self.refresh_browser_list()
    
    def refresh_translations(self):
        self.title.setText(tr("cleanup.title"))
        self.clean_btn.setText(tr("cleanup.clean_all"))
        self.loading_label.setText(tr("common.loading"))
