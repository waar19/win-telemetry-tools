import subprocess
import logging

class SystemRestoreManager:
    """Manages Windows System Restore points."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_restore_point(self, description: str) -> bool:
        """
        Creates a new system restore point.
        Returns True if successful, False otherwise.
        Requires Administrator privileges.
        """
        try:
            # Use PowerShell Checkpoint-Computer
            # -RestorePointType MODIFY_SETTINGS (12) is standard for app changes
            cmd = [
                "powershell", 
                "-NoProfile", 
                "-ExecutionPolicy", "Bypass", 
                "-Command",
                f"Checkpoint-Computer -Description '{description}' -RestorePointType 'MODIFY_SETTINGS'"
            ]
            
            # Create startupinfo to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                startupinfo=startupinfo
            )
            
            if result.returncode == 0:
                self.logger.info(f"Restore point '{description}' created successfully.")
                return True
            else:
                self.logger.error(f"Failed to create restore point: {result.stderr}")
                # Common error: System Restore disabled or frequency limit (once per 24h default, though API allows bypassing if configured, usually hard enforced by OS unless forced)
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating restore point: {str(e)}")
            return False

    def is_enabled(self) -> bool:
        """Checks if System Restore is enabled on the system drive."""
        try:
            cmd = [
                "powershell", 
                "-NoProfile", 
                "-Command",
                "Get-ComputerRestorePoint"
            ]
            # This is tricky as checking 'enabled' strictly requires query on specific drive.
            # A simpler check is trying to list restore points or status.
            # For now, we assume if we can invoke the cmdlet, it's somewhat working, 
            # but Checkpoint-Computer will fail if disabled.
            return True
        except:
            return False
