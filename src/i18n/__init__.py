"""
Internationalization (i18n) Module
Handles translations and language switching.
"""

import json
import os
import sys
import locale
from typing import Dict, Optional
from pathlib import Path


def get_i18n_dir() -> Path:
    """Get the i18n directory path, works both in dev and bundled mode."""
    if getattr(sys, 'frozen', False):
        # Running as bundled exe
        base_path = Path(sys._MEIPASS)
        return base_path / 'i18n'
    else:
        # Running in development
        return Path(__file__).parent


class Translator:
    """Handles loading and retrieving translations."""
    
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "es": "Español",
        "de": "Deutsch"
    }
    
    DEFAULT_LANGUAGE = "en"
    
    _instance: Optional['Translator'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._translations: Dict[str, Dict] = {}
        self._current_language = self.DEFAULT_LANGUAGE
        self._i18n_dir = get_i18n_dir()
        
        # Load all translations
        self._load_translations()
        
        # Detect system language
        self._detect_language()
    
    def _load_translations(self):
        """Load all translation files."""
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            file_path = self._i18n_dir / f"{lang_code}.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self._translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Error loading {lang_code}.json: {e}")
                    self._translations[lang_code] = {}
            else:
                print(f"Warning: Translation file not found: {file_path}")
    
    def _detect_language(self):
        """Detect system language and set if supported."""
        try:
            # Get system locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0].lower()
                if lang_code in self.SUPPORTED_LANGUAGES:
                    self._current_language = lang_code
        except Exception:
            pass
    
    def set_language(self, lang_code: str) -> bool:
        """Set the current language."""
        if lang_code in self.SUPPORTED_LANGUAGES:
            self._current_language = lang_code
            return True
        return False
    
    def get_language(self) -> str:
        """Get current language code."""
        return self._current_language
    
    def get_language_name(self) -> str:
        """Get current language display name."""
        return self.SUPPORTED_LANGUAGES.get(self._current_language, "English")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Get a translation by key.
        Key format: 'section.subsection.key' (e.g., 'nav.dashboard')
        """
        # Try current language first
        value = self._get_nested(self._translations.get(self._current_language, {}), key)
        
        # Fallback to English
        if value is None and self._current_language != self.DEFAULT_LANGUAGE:
            value = self._get_nested(self._translations.get(self.DEFAULT_LANGUAGE, {}), key)
        
        # Return default or key if not found
        if value is None:
            return default if default is not None else key
        
        return value
    
    def _get_nested(self, data: dict, key: str) -> Optional[str]:
        """Get nested value from dict using dot notation."""
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value if isinstance(value, str) else None
    
    def reload(self):
        """Reload translations from files."""
        self._translations.clear()
        self._load_translations()


# Global translator instance
_translator = Translator()


def tr(key: str, default: Optional[str] = None) -> str:
    """
    Shortcut function to get translation.
    Usage: tr("nav.dashboard") -> "Dashboard"
    """
    return _translator.get(key, default)


def set_language(lang_code: str) -> bool:
    """Set application language."""
    return _translator.set_language(lang_code)


def get_language() -> str:
    """Get current language code."""
    return _translator.get_language()


def get_available_languages() -> Dict[str, str]:
    """Get dict of available languages {code: name}."""
    return Translator.SUPPORTED_LANGUAGES.copy()
