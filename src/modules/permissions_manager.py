"""
Permissions Manager Module
Manages app permissions for camera, microphone, location, etc.
"""

import winreg
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PermissionType(Enum):
    """Types of permissions that can be managed."""
    CAMERA = "webcam"
    MICROPHONE = "microphone"
    LOCATION = "location"
    NOTIFICATIONS = "userNotificationListener"
    ACCOUNT_INFO = "userAccountInformation"
    CONTACTS = "contacts"
    CALENDAR = "appointments"
    PHONE_CALLS = "phoneCall"
    CALL_HISTORY = "phoneCallHistory"
    EMAIL = "email"
    TASKS = "userDataTasks"
    MESSAGING = "chat"
    RADIOS = "radios"
    BLUETOOTH = "bluetoothSync"
    APP_DIAGNOSTICS = "appDiagnostics"
    DOCUMENTS = "documentsLibrary"
    PICTURES = "picturesLibrary"
    VIDEOS = "videosLibrary"
    FILE_SYSTEM = "broadFileSystemAccess"


@dataclass
class PermissionStatus:
    """Status of a permission type."""
    permission_type: PermissionType
    display_name: str
    description: str
    is_enabled: bool
    apps_with_access: List[str]


@dataclass
class AppPermission:
    """Permission for a specific app."""
    app_name: str
    package_family_name: str
    permission_type: PermissionType
    is_allowed: bool


class PermissionsManager:
    """Manages Windows app permissions."""
    
    PERMISSION_REGISTRY_BASE = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore"
    
    PERMISSION_DISPLAY_NAMES = {
        PermissionType.CAMERA: ("Camera", "Allow apps to access your camera"),
        PermissionType.MICROPHONE: ("Microphone", "Allow apps to access your microphone"),
        PermissionType.LOCATION: ("Location", "Allow apps to access your location"),
        PermissionType.NOTIFICATIONS: ("Notifications", "Allow apps to read your notifications"),
        PermissionType.ACCOUNT_INFO: ("Account Info", "Allow apps to access your account information"),
        PermissionType.CONTACTS: ("Contacts", "Allow apps to access your contacts"),
        PermissionType.CALENDAR: ("Calendar", "Allow apps to access your calendar"),
        PermissionType.PHONE_CALLS: ("Phone Calls", "Allow apps to make phone calls"),
        PermissionType.CALL_HISTORY: ("Call History", "Allow apps to access call history"),
        PermissionType.EMAIL: ("Email", "Allow apps to access your email"),
        PermissionType.TASKS: ("Tasks", "Allow apps to access your tasks"),
        PermissionType.MESSAGING: ("Messaging", "Allow apps to read or send messages"),
        PermissionType.RADIOS: ("Radios", "Allow apps to control device radios"),
        PermissionType.BLUETOOTH: ("Bluetooth", "Allow apps to access Bluetooth"),
        PermissionType.APP_DIAGNOSTICS: ("App Diagnostics", "Allow apps to access diagnostic info"),
        PermissionType.DOCUMENTS: ("Documents", "Allow apps to access documents library"),
        PermissionType.PICTURES: ("Pictures", "Allow apps to access pictures library"),
        PermissionType.VIDEOS: ("Videos", "Allow apps to access videos library"),
        PermissionType.FILE_SYSTEM: ("File System", "Allow apps to access the file system"),
    }
    
    # Main permissions to show in UI
    MAIN_PERMISSIONS = [
        PermissionType.CAMERA,
        PermissionType.MICROPHONE,
        PermissionType.LOCATION,
        PermissionType.NOTIFICATIONS,
        PermissionType.CONTACTS,
        PermissionType.CALENDAR,
    ]
    
    def __init__(self):
        self._cache: Dict[PermissionType, PermissionStatus] = {}
    
    def get_all_permissions_status(self) -> List[PermissionStatus]:
        """Get status of all permission types."""
        statuses = []
        for perm_type in self.MAIN_PERMISSIONS:
            status = self.get_permission_status(perm_type)
            if status:
                statuses.append(status)
        return statuses
    
    def get_permission_status(self, permission_type: PermissionType) -> Optional[PermissionStatus]:
        """Get the status of a specific permission type."""
        try:
            reg_path = f"{self.PERMISSION_REGISTRY_BASE}\\{permission_type.value}"
            
            # Check global setting
            is_enabled = self._get_permission_global_state(reg_path)
            
            # Get apps with access
            apps = self._get_apps_with_permission(reg_path)
            
            display_name, description = self.PERMISSION_DISPLAY_NAMES.get(
                permission_type, 
                (permission_type.name, "")
            )
            
            return PermissionStatus(
                permission_type=permission_type,
                display_name=display_name,
                description=description,
                is_enabled=is_enabled,
                apps_with_access=apps
            )
        except Exception:
            return None
    
    def set_permission_global_state(self, permission_type: PermissionType, enabled: bool) -> Tuple[bool, str]:
        """Enable or disable a permission globally."""
        try:
            reg_path = f"{self.PERMISSION_REGISTRY_BASE}\\{permission_type.value}"
            value = "Allow" if enabled else "Deny"
            
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                reg_path,
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
            
            return True, f"Permission {'enabled' if enabled else 'disabled'}"
        except WindowsError as e:
            return False, str(e)
    
    def get_apps_for_permission(self, permission_type: PermissionType) -> List[AppPermission]:
        """Get all apps and their access status for a permission type."""
        apps = []
        try:
            reg_path = f"{self.PERMISSION_REGISTRY_BASE}\\{permission_type.value}"
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                reg_path,
                0,
                winreg.KEY_READ
            )
            
            # Enumerate subkeys (apps)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    if subkey_name not in ["NonPackaged"]:
                        app_key = winreg.OpenKey(key, subkey_name)
                        try:
                            value, _ = winreg.QueryValueEx(app_key, "Value")
                            is_allowed = value == "Allow"
                        except WindowsError:
                            is_allowed = False
                        winreg.CloseKey(app_key)
                        
                        # Clean up app name
                        app_name = self._clean_app_name(subkey_name)
                        
                        apps.append(AppPermission(
                            app_name=app_name,
                            package_family_name=subkey_name,
                            permission_type=permission_type,
                            is_allowed=is_allowed
                        ))
                    i += 1
                except WindowsError:
                    break
            
            winreg.CloseKey(key)
        except WindowsError:
            pass
        
        return apps
    
    def set_app_permission(self, permission_type: PermissionType, 
                           package_family_name: str, allowed: bool) -> Tuple[bool, str]:
        """Set permission for a specific app."""
        try:
            reg_path = f"{self.PERMISSION_REGISTRY_BASE}\\{permission_type.value}\\{package_family_name}"
            value = "Allow" if allowed else "Deny"
            
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                reg_path,
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
            
            return True, f"App permission {'allowed' if allowed else 'denied'}"
        except WindowsError as e:
            return False, str(e)
    
    def disable_all_permissions(self) -> Tuple[bool, str]:
        """Disable all permissions globally."""
        errors = []
        for perm_type in self.MAIN_PERMISSIONS:
            success, error = self.set_permission_global_state(perm_type, False)
            if not success:
                errors.append(f"{perm_type.name}: {error}")
        
        if errors:
            return False, "\n".join(errors)
        return True, "All permissions disabled"
    
    def get_privacy_score(self) -> int:
        """Calculate privacy score based on disabled permissions (0-100)."""
        statuses = self.get_all_permissions_status()
        if not statuses:
            return 100  # No permissions found = maximum privacy
        
        disabled_count = sum(1 for s in statuses if not s.is_enabled)
        return int((disabled_count / len(statuses)) * 100)
    
    def _get_permission_global_state(self, reg_path: str) -> bool:
        """Get the global state of a permission."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                reg_path,
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, "Value")
            winreg.CloseKey(key)
            return value == "Allow"
        except WindowsError:
            return True  # Default is usually allowed
    
    def _get_apps_with_permission(self, reg_path: str) -> List[str]:
        """Get list of apps with access to a permission."""
        apps = []
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                reg_path,
                0,
                winreg.KEY_READ
            )
            
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    if subkey_name not in ["NonPackaged"]:
                        apps.append(self._clean_app_name(subkey_name))
                    i += 1
                except WindowsError:
                    break
            
            winreg.CloseKey(key)
        except WindowsError:
            pass
        
        return apps
    
    def _clean_app_name(self, package_name: str) -> str:
        """Clean up package name to readable app name."""
        # Remove common prefixes and suffixes
        name = package_name
        if "_" in name:
            name = name.split("_")[0]
        
        # Split by dots and get last meaningful part
        parts = name.split(".")
        if len(parts) > 1:
            name = parts[-1]
        
        # Convert camelCase to spaces
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1 \2', name)
        
        return name.strip()
