"""
Settings Panel
UI for application settings including language selection, profiles, and auto-start.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QComboBox, QPushButton, QCheckBox,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from .styles import COLORS
from ..i18n import tr, set_language, get_language, get_available_languages
from ..modules.profile_manager import ProfileManager


class SettingsPanel(QWidget):
    """Panel for application settings."""
    
    language_changed = pyqtSignal(str)
    profile_imported = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile_mgr = ProfileManager()
        self._setup_ui()
        self._load_settings()
    
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
        self.title = QLabel(tr("settings.title"))
        self.title.setObjectName("sectionTitle")
        self.subtitle = QLabel(tr("settings.subtitle"))
        self.subtitle.setObjectName("subtitle")
        
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        
        # Language Setting
        lang_card = QFrame()
        lang_card.setObjectName("card")
        lang_layout = QHBoxLayout(lang_card)
        
        lang_info = QVBoxLayout()
        self.lang_label = QLabel(tr("settings.language"))
        self.lang_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.lang_desc = QLabel(tr("settings.language_desc"))
        self.lang_desc.setObjectName("muted")
        lang_info.addWidget(self.lang_label)
        lang_info.addWidget(self.lang_desc)
        
        self.lang_combo = QComboBox()
        self.lang_combo.setMinimumWidth(150)
        
        # Populate languages
        languages = get_available_languages()
        current_lang = get_language()
        
        for code, name in languages.items():
            self.lang_combo.addItem(name, code)
            if code == current_lang:
                self.lang_combo.setCurrentText(name)
        
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        
        lang_layout.addLayout(lang_info)
        lang_layout.addStretch()
        lang_layout.addWidget(self.lang_combo)
        
        layout.addWidget(lang_card)
        
        # Auto-Start Setting
        autostart_card = QFrame()
        autostart_card.setObjectName("card")
        autostart_layout = QHBoxLayout(autostart_card)
        
        autostart_info = QVBoxLayout()
        self.autostart_label = QLabel("Auto-Start")
        self.autostart_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.autostart_desc = QLabel("Launch Privacy Dashboard when Windows starts")
        self.autostart_desc.setObjectName("muted")
        autostart_info.addWidget(self.autostart_label)
        autostart_info.addWidget(self.autostart_desc)
        
        self.autostart_toggle = QCheckBox()
        self.autostart_toggle.setObjectName("toggle")
        self.autostart_toggle.toggled.connect(self._on_autostart_toggled)
        
        autostart_layout.addLayout(autostart_info)
        autostart_layout.addStretch()
        autostart_layout.addWidget(self.autostart_toggle)
        
        layout.addWidget(autostart_card)
        
        # Profile Management
        profile_card = QFrame()
        profile_card.setObjectName("card")
        profile_layout = QVBoxLayout(profile_card)
        
        profile_header = QHBoxLayout()
        profile_info = QVBoxLayout()
        self.profile_label = QLabel("Privacy Profile")
        self.profile_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.profile_desc = QLabel("Export or import your privacy settings")
        self.profile_desc.setObjectName("muted")
        profile_info.addWidget(self.profile_label)
        profile_info.addWidget(self.profile_desc)
        profile_header.addLayout(profile_info)
        profile_header.addStretch()
        profile_layout.addLayout(profile_header)
        
        # Profile buttons
        btn_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export Profile")
        self.export_btn.setObjectName("secondary")
        self.export_btn.clicked.connect(self._export_profile)
        
        self.import_btn = QPushButton("Import Profile")
        self.import_btn.clicked.connect(self._import_profile)
        
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addStretch()
        
        profile_layout.addLayout(btn_layout)
        layout.addWidget(profile_card)
        
        # Note
        self.note_label = QLabel(tr("settings.restart_note"))
        self.note_label.setObjectName("muted")
        self.note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.note_label)
        
        layout.addStretch()
    
    def _load_settings(self):
        """Load current settings."""
        # Check auto-start status
        self.autostart_toggle.blockSignals(True)
        self.autostart_toggle.setChecked(self.profile_mgr.is_autostart_enabled())
        self.autostart_toggle.blockSignals(False)
    
    def _on_language_changed(self, index):
        lang_code = self.lang_combo.currentData()
        if lang_code and set_language(lang_code):
            self.language_changed.emit(lang_code)
            self._update_texts()
    
    def _on_autostart_toggled(self, checked):
        if checked:
            success, msg = self.profile_mgr.enable_autostart()
        else:
            success, msg = self.profile_mgr.disable_autostart()
        
        if not success:
            QMessageBox.warning(self, "Error", msg)
            self.autostart_toggle.blockSignals(True)
            self.autostart_toggle.setChecked(not checked)
            self.autostart_toggle.blockSignals(False)
    
    def _export_profile(self):
        """Export current profile to file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Privacy Profile",
            "privacy_profile.json",
            "JSON Files (*.json)"
        )
        
        if filepath:
            # Collect current settings
            profile_data = {
                "language": get_language(),
                "autostart": self.profile_mgr.is_autostart_enabled()
            }
            
            success, msg = self.profile_mgr.export_profile(filepath, profile_data)
            if success:
                QMessageBox.information(self, "Success", "Profile exported successfully!")
            else:
                QMessageBox.warning(self, "Error", msg)
    
    def _import_profile(self):
        """Import profile from file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import Privacy Profile",
            "",
            "JSON Files (*.json)"
        )
        
        if filepath:
            success, data, msg = self.profile_mgr.import_profile(filepath)
            if success and data:
                # Apply settings
                if "language" in data:
                    set_language(data["language"])
                    self._update_texts()
                
                if "autostart" in data:
                    if data["autostart"]:
                        self.profile_mgr.enable_autostart()
                    else:
                        self.profile_mgr.disable_autostart()
                    self._load_settings()
                
                self.profile_imported.emit(data)
                QMessageBox.information(self, "Success", "Profile imported successfully!")
            else:
                QMessageBox.warning(self, "Error", msg)
    
    def _update_texts(self):
        """Update all text with new translations."""
        self.title.setText(tr("settings.title"))
        self.subtitle.setText(tr("settings.subtitle"))
        self.lang_label.setText(tr("settings.language"))
        self.lang_desc.setText(tr("settings.language_desc"))
        self.note_label.setText(tr("settings.restart_note"))
    
    def refresh_translations(self):
        """Called when language changes from outside."""
        self._update_texts()
    
    def get_profile_data(self) -> dict:
        """Get current profile data for export."""
        return {
            "language": get_language(),
            "autostart": self.profile_mgr.is_autostart_enabled()
        }
