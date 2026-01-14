"""
Tracking Cleaner Module
Cleans Windows tracking data, activity history, and resets advertising ID.
"""

import os
import shutil
import subprocess
import winreg
import uuid
from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CleanupItem:
    """Represents a cleanup target."""
    name: str
    description: str
    category: str
    size_bytes: int = 0
    can_clean: bool = True


class TrackingCleaner:
    """Handles cleaning of Windows tracking and activity data."""
    
    # Directories to clean
    CLEANUP_TARGETS = {
        "prefetch": {
            "path": r"C:\Windows\Prefetch",
            "name": "Prefetch Cache",
            "description": "Windows application launch cache",
            "category": "System Cache"
        },
        "recent": {
            "path": os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Recent"),
            "name": "Recent Files",
            "description": "Recent file access history",
            "category": "Activity History"
        },
        "temp": {
            "path": os.path.expandvars(r"%TEMP%"),
            "name": "Temporary Files",
            "description": "Temporary system files",
            "category": "System Cache"
        },
        "temp_win": {
            "path": r"C:\Windows\Temp",
            "name": "Windows Temp",
            "description": "Windows temporary files",
            "category": "System Cache"
        },
        "thumbnail_cache": {
            "path": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer"),
            "name": "Thumbnail Cache",
            "description": "Image thumbnail cache files",
            "category": "System Cache"
        },
        "icon_cache": {
            "path": os.path.expandvars(r"%LOCALAPPDATA%\IconCache.db"),
            "name": "Icon Cache",
            "description": "Application icon cache",
            "category": "System Cache"
        },
        "font_cache": {
            "path": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\FontCache"),
            "name": "Font Cache",
            "description": "Font rendering cache",
            "category": "System Cache"
        },
    }
    
    # Registry-based tracking data
    REGISTRY_CLEANUP = [
        {
            "name": "Windows Search History",
            "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery",
            "hive": winreg.HKEY_CURRENT_USER,
            "category": "Activity History"
        },
        {
            "name": "Run Dialog History",
            "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
            "hive": winreg.HKEY_CURRENT_USER,
            "category": "Activity History"
        },
        {
            "name": "Typed Paths History",
            "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths",
            "hive": winreg.HKEY_CURRENT_USER,
            "category": "Activity History"
        },
    ]
    
    def __init__(self):
        self._cache: Dict[str, int] = {}
    
    def get_cleanup_status(self) -> List[CleanupItem]:
        """Get all cleanup targets with their current sizes."""
        items = []
        
        # Check directory targets
        for key, target in self.CLEANUP_TARGETS.items():
            path = target["path"]
            size = self._get_directory_size(path)
            items.append(CleanupItem(
                name=target["name"],
                description=target["description"],
                category=target["category"],
                size_bytes=size,
                can_clean=os.path.exists(path)
            ))
        
        # Check registry targets
        for reg_target in self.REGISTRY_CLEANUP:
            has_data = self._check_registry_has_data(reg_target)
            items.append(CleanupItem(
                name=reg_target["name"],
                description=f"Registry: {reg_target['path']}",
                category=reg_target["category"],
                size_bytes=0,
                can_clean=has_data
            ))
        
        # Add advertising ID
        items.append(CleanupItem(
            name="Advertising ID",
            description="Reset Windows Advertising ID",
            category="Tracking",
            size_bytes=0,
            can_clean=True
        ))
        
        # Add Activity History
        items.append(CleanupItem(
            name="Activity History",
            description="Windows Timeline activity history",
            category="Activity History",
            size_bytes=0,
            can_clean=True
        ))
        
        return items
    
    def get_total_cleanup_size(self) -> int:
        """Get total size of data that can be cleaned."""
        items = self.get_cleanup_status()
        return sum(item.size_bytes for item in items)
    
    def clean_all(self, progress_callback=None) -> Tuple[bool, str, int]:
        """Clean all tracking data. Returns success, message, and bytes cleaned."""
        errors = []
        total_cleaned = 0
        total_items = len(self.CLEANUP_TARGETS) + len(self.REGISTRY_CLEANUP) + 2  # +2 for ad ID and activity
        current_item = 0
        
        # Clean directory targets
        for key, target in self.CLEANUP_TARGETS.items():
            current_item += 1
            if progress_callback:
                progress_callback(current_item, total_items, target["name"])
            
            success, cleaned = self._clean_directory(target["path"])
            if success:
                total_cleaned += cleaned
            else:
                errors.append(f"Failed to clean {target['name']}")
        
        # Clean registry targets
        for reg_target in self.REGISTRY_CLEANUP:
            current_item += 1
            if progress_callback:
                progress_callback(current_item, total_items, reg_target["name"])
            
            success, error = self._clean_registry_key(reg_target)
            if not success and error:
                errors.append(f"{reg_target['name']}: {error}")
        
        # Reset Advertising ID
        current_item += 1
        if progress_callback:
            progress_callback(current_item, total_items, "Advertising ID")
        success, error = self.reset_advertising_id()
        if not success:
            errors.append(f"Advertising ID: {error}")
        
        # Clear Activity History
        current_item += 1
        if progress_callback:
            progress_callback(current_item, total_items, "Activity History")
        success, error = self.clear_activity_history()
        if not success:
            errors.append(f"Activity History: {error}")
        
        if errors:
            return False, "\n".join(errors), total_cleaned
        return True, f"Cleaned {self._format_size(total_cleaned)}", total_cleaned
    
    def clean_category(self, category: str) -> Tuple[bool, str]:
        """Clean all items in a specific category."""
        errors = []
        
        # Clean matching directory targets
        for key, target in self.CLEANUP_TARGETS.items():
            if target["category"] == category:
                success, _ = self._clean_directory(target["path"])
                if not success:
                    errors.append(f"Failed to clean {target['name']}")
        
        # Clean matching registry targets
        for reg_target in self.REGISTRY_CLEANUP:
            if reg_target["category"] == category:
                success, error = self._clean_registry_key(reg_target)
                if not success and error:
                    errors.append(error)
        
        if errors:
            return False, "\n".join(errors)
        return True, f"Category '{category}' cleaned"
    
    def reset_advertising_id(self) -> Tuple[bool, str]:
        """Reset the Windows Advertising ID."""
        try:
            # Generate new advertising ID
            new_id = str(uuid.uuid4()).upper()
            
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "Id", 0, winreg.REG_SZ, new_id)
            winreg.CloseKey(key)
            
            return True, f"Advertising ID reset to {new_id[:8]}..."
        except WindowsError as e:
            return False, str(e)
    
    def clear_activity_history(self) -> Tuple[bool, str]:
        """Clear Windows Activity History."""
        try:
            # Delete activity history database
            activity_path = os.path.expandvars(
                r"%LOCALAPPDATA%\ConnectedDevicesPlatform"
            )
            
            if os.path.exists(activity_path):
                for root, dirs, files in os.walk(activity_path):
                    for file in files:
                        if file.endswith(".db") or file.endswith(".db-wal") or file.endswith(".db-shm"):
                            try:
                                os.remove(os.path.join(root, file))
                            except Exception:
                                pass
            
            # Disable activity history via registry
            key = winreg.CreateKeyEx(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\System",
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
            )
            winreg.SetValueEx(key, "EnableActivityFeed", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "PublishUserActivities", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "UploadUserActivities", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            return True, "Activity History cleared"
        except Exception as e:
            return False, str(e)
    
    def disable_activity_history(self) -> Tuple[bool, str]:
        """Disable Activity History collection."""
        try:
            key = winreg.CreateKeyEx(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\System",
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
            )
            winreg.SetValueEx(key, "EnableActivityFeed", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "PublishUserActivities", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "UploadUserActivities", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            return True, "Activity History disabled"
        except WindowsError as e:
            return False, str(e)
    
    def _get_directory_size(self, path: str) -> int:
        """Get the size of a directory in bytes."""
        total_size = 0
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return total_size
    
    def _clean_directory(self, path: str) -> Tuple[bool, int]:
        """Clean a directory and return bytes cleaned."""
        cleaned = 0
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                os.remove(path)
                return True, size
            
            if not os.path.exists(path):
                return True, 0
            
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path)
                        os.remove(item_path)
                        cleaned += size
                    elif os.path.isdir(item_path):
                        size = self._get_directory_size(item_path)
                        shutil.rmtree(item_path, ignore_errors=True)
                        cleaned += size
                except (OSError, PermissionError):
                    pass
            
            return True, cleaned
        except Exception:
            return False, cleaned
    
    def _check_registry_has_data(self, reg_target: dict) -> bool:
        """Check if a registry key has data to clean."""
        try:
            key = winreg.OpenKey(
                reg_target["hive"],
                reg_target["path"],
                0,
                winreg.KEY_READ
            )
            # Check if key has values
            _, num_values, _ = winreg.QueryInfoKey(key)
            winreg.CloseKey(key)
            return num_values > 0
        except WindowsError:
            return False
    
    def _clean_registry_key(self, reg_target: dict) -> Tuple[bool, str]:
        """Clean a registry key by deleting all its values."""
        try:
            key = winreg.OpenKey(
                reg_target["hive"],
                reg_target["path"],
                0,
                winreg.KEY_ALL_ACCESS
            )
            
            # Get all value names
            values_to_delete = []
            i = 0
            while True:
                try:
                    value_name, _, _ = winreg.EnumValue(key, i)
                    if value_name != "MRUListEx":  # Keep the list structure
                        values_to_delete.append(value_name)
                    i += 1
                except WindowsError:
                    break
            
            # Delete values
            for value_name in values_to_delete:
                try:
                    winreg.DeleteValue(key, value_name)
                except WindowsError:
                    pass
            
            winreg.CloseKey(key)
            return True, ""
        except WindowsError as e:
            if "cannot find" in str(e).lower():
                return True, ""  # Key doesn't exist, nothing to clean
            return False, str(e)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes as human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
