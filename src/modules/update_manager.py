"""
Windows Update Manager Module
Manages Windows Update policies via Registry.
"""

import winreg
from typing import Tuple, Optional


class UpdateManager:
    """Manages Windows Update settings."""
    
    KEY_PATH = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
    
    # AUOptions values:
    # 2 = Notify before download.
    # 3 = Automatically download and notify of installation.
    # 4 = Auotmatically download and schedule installation.
    # 5 = Automatic Updates is required, but end users can configure it.
    
    def _get_key(self, write: bool = False):
        """Get registry key, create if necessary."""
        access = winreg.KEY_ALL_ACCESS if write else winreg.KEY_READ
        try:
            return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.KEY_PATH, 0, access)
        except WindowsError:
            if write:
                # Create key if not exists
                base = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate")
                key = winreg.CreateKey(base, "AU")
                return key
            return None

    def get_status(self) -> dict:
        """Get current update settings."""
        status = {
            "no_auto_update": False,
            "au_options": 0,
            "configured": False
        }
        
        try:
            key = self._get_key()
            if key:
                status["configured"] = True
                try:
                    val, _ = winreg.QueryValueEx(key, "NoAutoUpdate")
                    status["no_auto_update"] = bool(val)
                except WindowsError:
                    pass
                
                try:
                    val, _ = winreg.QueryValueEx(key, "AUOptions")
                    status["au_options"] = int(val)
                except WindowsError:
                    pass
                
                winreg.CloseKey(key)
        except Exception as e:
            print(f"Error reading update status: {e}")
            
        return status
    
    def disable_auto_updates(self) -> Tuple[bool, str]:
        """Disable automatic updates entirely."""
        try:
            key = self._get_key(write=True)
            winreg.SetValueEx(key, "NoAutoUpdate", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            return True, "Automatic updates disabled"
        except Exception as e:
            return False, f"Failed to disable updates: {e}"
    
    def set_notify_only(self) -> Tuple[bool, str]:
        """Set updates to notify only (don't download automatically)."""
        try:
            key = self._get_key(write=True)
            winreg.SetValueEx(key, "NoAutoUpdate", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "AUOptions", 0, winreg.REG_DWORD, 2)
            winreg.CloseKey(key)
            return True, "Updates set to 'Notify Only'"
        except Exception as e:
            return False, f"Failed to set notify only: {e}"
    
    def restore_defaults(self) -> Tuple[bool, str]:
        """Remove policies (restore Windows defaults)."""
        try:
            key = self._get_key(write=True)
            try:
                winreg.DeleteValue(key, "NoAutoUpdate")
            except WindowsError: pass
            
            try:
                winreg.DeleteValue(key, "AUOptions")
            except WindowsError: pass
            
            winreg.CloseKey(key)
            return True, "Restored default update settings"
        except Exception as e:
            return False, f"Failed to restore defaults: {e}"
