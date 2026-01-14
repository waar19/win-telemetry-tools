"""
Telemetry Blocker Module
Manages Windows telemetry settings, services, and scheduled tasks.
"""

import winreg
import subprocess
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class TelemetryItem:
    """Represents a telemetry setting or service."""
    name: str
    description: str
    category: str
    is_blocked: bool = False


class TelemetryBlocker:
    """Handles blocking/unblocking of Windows telemetry."""
    
    # Registry keys for telemetry settings
    TELEMETRY_REGISTRY_KEYS = [
        {
            "path": r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            "name": "AllowTelemetry",
            "blocked_value": 0,
            "unblocked_value": 3,
            "description": "Windows Telemetry Level"
        },
        {
            "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection",
            "name": "AllowTelemetry",
            "blocked_value": 0,
            "unblocked_value": 3,
            "description": "Data Collection Policy"
        },
        {
            "path": r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            "name": "DoNotShowFeedbackNotifications",
            "blocked_value": 1,
            "unblocked_value": 0,
            "description": "Feedback Notifications"
        },
        {
            "path": r"SOFTWARE\Policies\Microsoft\Windows\CloudContent",
            "name": "DisableTailoredExperiencesWithDiagnosticData",
            "blocked_value": 1,
            "unblocked_value": 0,
            "description": "Tailored Experiences"
        },
        {
            "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
            "name": "Enabled",
            "blocked_value": 0,
            "unblocked_value": 1,
            "description": "Advertising ID"
        },
    ]
    
    # Services related to telemetry
    TELEMETRY_SERVICES = [
        {
            "name": "DiagTrack",
            "display_name": "Connected User Experiences and Telemetry",
            "description": "Main telemetry service"
        },
        {
            "name": "dmwappushservice",
            "display_name": "Device Management WAP Push Service",
            "description": "Push message routing service"
        },
        {
            "name": "diagnosticshub.standardcollector.service",
            "display_name": "Diagnostics Hub Standard Collector",
            "description": "Diagnostics data collection"
        },
    ]
    
    # Scheduled tasks related to telemetry
    TELEMETRY_TASKS = [
        r"\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
        r"\Microsoft\Windows\Application Experience\ProgramDataUpdater",
        r"\Microsoft\Windows\Autochk\Proxy",
        r"\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
        r"\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
        r"\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector",
        r"\Microsoft\Windows\Feedback\Siuf\DmClient",
        r"\Microsoft\Windows\Feedback\Siuf\DmClientOnScenarioDownload",
    ]
    
    def __init__(self):
        self._cache_status: Dict[str, bool] = {}
    
    def get_telemetry_status(self) -> List[TelemetryItem]:
        """Get the current status of all telemetry settings."""
        items = []
        
        # Check registry settings
        for reg_key in self.TELEMETRY_REGISTRY_KEYS:
            is_blocked = self._check_registry_blocked(reg_key)
            items.append(TelemetryItem(
                name=reg_key["description"],
                description=f"Registry: {reg_key['path']}\\{reg_key['name']}",
                category="Registry",
                is_blocked=is_blocked
            ))
        
        # Check services
        for service in self.TELEMETRY_SERVICES:
            is_blocked = self._check_service_disabled(service["name"])
            items.append(TelemetryItem(
                name=service["display_name"],
                description=service["description"],
                category="Service",
                is_blocked=is_blocked
            ))
        
        # Check scheduled tasks
        for task in self.TELEMETRY_TASKS:
            task_name = task.split("\\")[-1]
            is_blocked = self._check_task_disabled(task)
            items.append(TelemetryItem(
                name=task_name,
                description=f"Scheduled Task: {task}",
                category="Task",
                is_blocked=is_blocked
            ))
        
        return items
    
    def get_privacy_score(self) -> int:
        """Calculate privacy score based on blocked items (0-100)."""
        items = self.get_telemetry_status()
        if not items:
            return 0
        blocked_count = sum(1 for item in items if item.is_blocked)
        return int((blocked_count / len(items)) * 100)
    
    def block_all_telemetry(self) -> Tuple[bool, str]:
        """Block all telemetry settings."""
        errors = []
        
        # Block registry settings
        for reg_key in self.TELEMETRY_REGISTRY_KEYS:
            success, error = self._set_registry_value(
                reg_key["path"],
                reg_key["name"],
                reg_key["blocked_value"]
            )
            if not success:
                errors.append(f"Registry {reg_key['name']}: {error}")
        
        # Disable services
        for service in self.TELEMETRY_SERVICES:
            success, error = self._disable_service(service["name"])
            if not success:
                errors.append(f"Service {service['name']}: {error}")
        
        # Disable scheduled tasks
        for task in self.TELEMETRY_TASKS:
            success, error = self._disable_task(task)
            if not success:
                errors.append(f"Task {task}: {error}")
        
        if errors:
            return False, "\n".join(errors)
        return True, "All telemetry blocked successfully"
    
    def unblock_all_telemetry(self) -> Tuple[bool, str]:
        """Restore default telemetry settings."""
        errors = []
        
        # Restore registry settings
        for reg_key in self.TELEMETRY_REGISTRY_KEYS:
            success, error = self._set_registry_value(
                reg_key["path"],
                reg_key["name"],
                reg_key["unblocked_value"]
            )
            if not success:
                errors.append(f"Registry {reg_key['name']}: {error}")
        
        # Enable services
        for service in self.TELEMETRY_SERVICES:
            success, error = self._enable_service(service["name"])
            if not success:
                errors.append(f"Service {service['name']}: {error}")
        
        # Enable scheduled tasks
        for task in self.TELEMETRY_TASKS:
            success, error = self._enable_task(task)
            if not success:
                errors.append(f"Task {task}: {error}")
        
        if errors:
            return False, "\n".join(errors)
        return True, "Telemetry restored to defaults"
    
    def _check_registry_blocked(self, reg_key: dict) -> bool:
        """Check if a registry key is set to blocked value."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                reg_key["path"],
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, reg_key["name"])
            winreg.CloseKey(key)
            return value == reg_key["blocked_value"]
        except WindowsError:
            return False
    
    def _set_registry_value(self, path: str, name: str, value: int) -> Tuple[bool, str]:
        """Set a registry value."""
        try:
            key = winreg.CreateKeyEx(
                winreg.HKEY_LOCAL_MACHINE,
                path,
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
            )
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            return True, ""
        except WindowsError as e:
            return False, str(e)
    
    def _check_service_disabled(self, service_name: str) -> bool:
        """Check if a service is disabled."""
        try:
            result = subprocess.run(
                ["sc", "qc", service_name],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "DISABLED" in result.stdout or "4" in result.stdout
        except Exception:
            return False
    
    def _disable_service(self, service_name: str) -> Tuple[bool, str]:
        """Disable a Windows service."""
        try:
            # Stop the service first
            subprocess.run(
                ["sc", "stop", service_name],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            # Disable the service
            result = subprocess.run(
                ["sc", "config", service_name, "start=", "disabled"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return True, ""
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def _enable_service(self, service_name: str) -> Tuple[bool, str]:
        """Enable a Windows service."""
        try:
            result = subprocess.run(
                ["sc", "config", service_name, "start=", "auto"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                # Start the service
                subprocess.run(
                    ["sc", "start", service_name],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return True, ""
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def _check_task_disabled(self, task_path: str) -> bool:
        """Check if a scheduled task is disabled."""
        try:
            result = subprocess.run(
                ["schtasks", "/Query", "/TN", task_path, "/FO", "LIST"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "Disabled" in result.stdout
        except Exception:
            return False
    
    def _disable_task(self, task_path: str) -> Tuple[bool, str]:
        """Disable a scheduled task."""
        try:
            result = subprocess.run(
                ["schtasks", "/Change", "/TN", task_path, "/DISABLE"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return True, ""
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def _enable_task(self, task_path: str) -> Tuple[bool, str]:
        """Enable a scheduled task."""
        try:
            result = subprocess.run(
                ["schtasks", "/Change", "/TN", task_path, "/ENABLE"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return True, ""
            return False, result.stderr
        except Exception as e:
            return False, str(e)
