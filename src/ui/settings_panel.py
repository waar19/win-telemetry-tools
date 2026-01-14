"""
Settings Panel
UI for application settings including language selection.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from .styles import COLORS
from ..i18n import tr, set_language, get_language, get_available_languages


class SettingsPanel(QWidget):
    """Panel for application settings."""
    
    language_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
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
        
        # Note about language change
        self.note_label = QLabel(tr("settings.restart_note"))
        self.note_label.setObjectName("muted")
        self.note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.note_label)
        
        layout.addStretch()
    
    def _on_language_changed(self, index):
        lang_code = self.lang_combo.currentData()
        if lang_code and set_language(lang_code):
            self.language_changed.emit(lang_code)
            self._update_texts()
    
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
