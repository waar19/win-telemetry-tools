"""
Workers Module
Background workers for async data loading.
"""

from PyQt6.QtCore import QThread, pyqtSignal
from typing import Any, Callable


class DataLoaderWorker(QThread):
    """Generic worker for loading data in background."""
    
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, load_func: Callable, parent=None):
        super().__init__(parent)
        self.load_func = load_func
    
    def run(self):
        try:
            result = self.load_func()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class TelemetryDataWorker(QThread):
    """Worker for loading telemetry status."""
    
    finished = pyqtSignal(list)
    
    def __init__(self, blocker, parent=None):
        super().__init__(parent)
        self.blocker = blocker
    
    def run(self):
        items = self.blocker.get_telemetry_status()
        self.finished.emit(items)


class FirewallDataWorker(QThread):
    """Worker for loading firewall rules."""
    
    finished = pyqtSignal(list)
    
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
    
    def run(self):
        rules = self.manager.get_all_rules_status()
        self.finished.emit(rules)


class PermissionsDataWorker(QThread):
    """Worker for loading permissions status."""
    
    finished = pyqtSignal(object, list)  # status, apps
    
    def __init__(self, manager, permission_type, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.permission_type = permission_type
    
    def run(self):
        status = self.manager.get_permission_status(self.permission_type)
        apps = self.manager.get_apps_for_permission(self.permission_type)
        self.finished.emit(status, apps)


class CleanupDataWorker(QThread):
    """Worker for loading cleanup items."""
    
    finished = pyqtSignal(list)
    
    def __init__(self, cleaner, parent=None):
        super().__init__(parent)
        self.cleaner = cleaner
    
    def run(self):
        items = self.cleaner.get_cleanup_status()
        self.finished.emit(items)


class DashboardDataWorker(QThread):
    """Worker for loading dashboard stats."""
    
    finished = pyqtSignal(int, int, tuple, int)  # t_score, p_score, f_counts, c_size
    
    def __init__(self, telemetry, permissions, firewall, cleaner, parent=None):
        super().__init__(parent)
        self.telemetry = telemetry
        self.permissions = permissions
        self.firewall = firewall
        self.cleaner = cleaner
    
    def run(self):
        t_score = self.telemetry.get_privacy_score()
        p_score = self.permissions.get_privacy_score()
        f_counts = self.firewall.get_blocked_count()
        c_size = self.cleaner.get_total_cleanup_size()
        self.finished.emit(t_score, p_score, f_counts, c_size)


class RestoreWorker(QThread):
    """Worker for creating system restore points."""
    
    finished = pyqtSignal(bool, str)
    
    def __init__(self, manager, description, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.description = description
    
    def run(self):
        try:
            success = self.manager.create_restore_point(self.description)
            if success:
                self.finished.emit(True, "success") # Message will be localized in UI
            else:
                self.finished.emit(False, "error")
        except Exception as e:
            self.finished.emit(False, str(e))
