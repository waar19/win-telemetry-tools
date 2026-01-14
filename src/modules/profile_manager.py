"""
Profile Manager Module
Handles export/import of privacy settings and auto-start configuration.
"""

import json
import os
import sys
import winreg
from pathlib import Path
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PrivacyProfile:
    """Data structure for a privacy profile."""
    name: str
    created_at: str
    telemetry_blocked: bool
    permissions_restricted: bool
    firewall_enabled: bool
    blocked_endpoints: list
    settings: dict


class ProfileManager:
    """Manages privacy profiles and auto-start settings."""
    
    APP_NAME = "PrivacyDashboard"
    PROFILE_VERSION = "1.0"
    
    AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def __init__(self):
        self._app_data_dir = self._get_app_data_dir()
        self._profiles_dir = self._app_data_dir / "profiles"
        self._profiles_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_app_data_dir(self) -> Path:
        """Get or create app data directory."""
        if sys.platform == "win32":
            base = Path(os.environ.get("APPDATA", ""))
        else:
            base = Path.home() / ".config"
        
        app_dir = base / "PrivacyDashboard"
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
    
    def _get_exe_path(self) -> str:
        """Get the executable path."""
        if getattr(sys, 'frozen', False):
            return sys.executable
        else:
            # Development mode - return python script path
            return f'"{sys.executable}" "{Path(__file__).parent.parent / "main.py"}"'
    
    # ==================== Profile Export/Import ====================
    
    def export_profile(self, filepath: str, profile_data: dict) -> Tuple[bool, str]:
        """Export current settings to a JSON file."""
        try:
            profile = {
                "version": self.PROFILE_VERSION,
                "app": self.APP_NAME,
                "created_at": datetime.now().isoformat(),
                "data": profile_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            
            return True, f"Profile exported to {filepath}"
        except Exception as e:
            return False, str(e)
    
    def import_profile(self, filepath: str) -> Tuple[bool, Optional[dict], str]:
        """Import settings from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            # Validate profile
            if profile.get("app") != self.APP_NAME:
                return False, None, "Invalid profile: Not a Privacy Dashboard profile"
            
            return True, profile.get("data", {}), "Profile imported successfully"
        except json.JSONDecodeError:
            return False, None, "Invalid JSON file"
        except Exception as e:
            return False, None, str(e)
    
    def get_saved_profiles(self) -> list:
        """Get list of saved profiles in app directory."""
        profiles = []
        for f in self._profiles_dir.glob("*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    profiles.append({
                        "name": f.stem,
                        "path": str(f),
                        "created": data.get("created_at", "Unknown")
                    })
            except:
                pass
        return profiles
    
    # ==================== Auto-Start ====================
    
    def is_autostart_enabled(self) -> bool:
        """Check if app is set to run at Windows startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.AUTOSTART_KEY,
                0,
                winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True
            except WindowsError:
                winreg.CloseKey(key)
                return False
        except WindowsError:
            return False
    
    def enable_autostart(self) -> Tuple[bool, str]:
        """Enable app auto-start at Windows login."""
        try:
            exe_path = self._get_exe_path()
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.AUTOSTART_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            
            return True, "Auto-start enabled"
        except Exception as e:
            return False, str(e)
    
    def disable_autostart(self) -> Tuple[bool, str]:
        """Disable app auto-start."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.AUTOSTART_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            try:
                winreg.DeleteValue(key, self.APP_NAME)
            except WindowsError:
                pass  # Already doesn't exist
            winreg.CloseKey(key)
            
            return True, "Auto-start disabled"
        except Exception as e:
            return False, str(e)
    
    def get_app_data_path(self) -> Path:
        """Get the app data directory path."""
        return self._app_data_dir
