"""
Cleanup Panel
UI for cleaning tracking data.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QCheckBox, QPushButton,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal

from .styles import COLORS
from .workers import CleanupDataWorker
from ..modules.tracking_cleaner import TrackingCleaner, CleanupItem


class CleanWorker(QThread):
    """Worker thread for cleanup operations."""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(bool, str, int)
    
    def __init__(self, cleaner: TrackingCleaner):
        super().__init__()
        self.cleaner = cleaner
    
    def run(self):
        success, msg, bytes_cleaned = self.cleaner.clean_all(self.progress.emit)
        self.finished.emit(success, msg, bytes_cleaned)


class CleanupPanel(QWidget):
    """Panel for cleaning tracking data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cleaner = TrackingCleaner()
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
        title = QLabel("Tracking Cleanup")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("Remove activity history, cache, and tracking identifiers")
        subtitle.setObjectName("subtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        
        header_layout.addLayout(title_block)
        header_layout.addStretch()
        
        # Action
        self.clean_btn = QPushButton("Clean All")
        self.clean_btn.clicked.connect(self.start_cleanup)
        
        header_layout.addWidget(self.clean_btn)
        
        layout.addLayout(header_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)
        
        # Loading indicator
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setObjectName("muted")
        self.loading_label.setVisible(False)
        layout.addWidget(self.loading_label)
        
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
        """Reload cleanup items status in background."""
        if self._is_loading:
            return
        
        self._is_loading = True
        self.loading_label.setVisible(True)
        self.clean_btn.setEnabled(False)
        
        self._worker = CleanupDataWorker(self.cleaner)
        self._worker.finished.connect(self._on_data_loaded)
        self._worker.start()
    
    @pyqtSlot(list)
    def _on_data_loaded(self, items: list):
        """Handle loaded data."""
        self._is_loading = False
        self.loading_label.setVisible(False)
        self.clean_btn.setEnabled(True)
        
        # Clear existing items
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
    
    @pyqtSlot(int, int, str)
    def update_progress(self, current, total, item_name):
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(f"Cleaning: {item_name}")
    
    @pyqtSlot(bool, str, int)
    def cleanup_finished(self, success, msg, bytes_cleaned):
        self.clean_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        if success:
            cleaned_str = self.cleaner._format_size(bytes_cleaned)
            QMessageBox.information(self, "Cleanup Complete", 
                                  f"Successfully cleaned from system.\nFreed: {cleaned_str}")
        else:
            QMessageBox.warning(self, "Cleanup Warning", msg)
            
        self.refresh_data()
