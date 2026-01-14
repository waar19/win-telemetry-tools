import subprocess
import logging
import json

class AppManager:
    """Manages Windows AppX packages (Bloatware)."""
    
    # List of known bloatware keywords in PackageNames
    BLOATWARE_KEYWORDS = [
        "Microsoft.3DBuilder",
        "Microsoft.BingNews",
        "Microsoft.BingWeather",
        "Microsoft.Getstarted",
        "Microsoft.Microsoft3DViewer",
        "Microsoft.MicrosoftOfficeHub",
        "Microsoft.MicrosoftSolitaireCollection",
        "Microsoft.MixedReality.Portal",
        "Microsoft.OneConnect",
        "Microsoft.People",
        "Microsoft.SkypeApp",
        "Microsoft.Wallet",
        "Microsoft.WindowsFeedbackHub",
        "Microsoft.Xbox",
        "Microsoft.ZuneMusic",
        "Microsoft.ZuneVideo",
        "CandyCrush",
        "Netflix",
        "Spotify",
        "Disney",
        "Facebook",
        "Twitter",
        "Instagram",
        "TikTok"
    ]

    # Apps that should NOT be removed as they are critical or very common utilities
    CRITICAL_KEYWORDS = [
        "Microsoft.WindowsStore",
        "Microsoft.Windows.ShellExperienceHost",
        "Microsoft.Windows.StartMenuExperienceHost",
        "windows.immersivecontrolpanel",
        "Microsoft.Windows.Cortana",
        "Microsoft.Windows.SecHealthUI" # Defender UI
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_installed_apps(self) -> list:
        """
        Returns a list of installed AppX packages.
        Each item is a dict: {name, id, version, publisher, is_bloatware}
        """
        try:
            # Get list as JSON using PowerShell
            cmd = [
                "powershell", "-NoProfile", "-Command",
                "Get-AppxPackage | Select-Object Name, PackageFullName, Version, Publisher | ConvertTo-Json"
            ]
            
            # Hide window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
            
            if result.returncode != 0:
                self.logger.error("Failed to get apps list")
                return []
                
            data = json.loads(result.stdout)
            
            # If single item, PowerShell ConvertTo-Json returns dict, not list
            if isinstance(data, dict):
                data = [data]
                
            apps = []
            for item in data:
                name = item.get("Name", "")
                full_name = item.get("PackageFullName", "")
                
                # Determine if potential bloatware or critical
                is_bloat = any(k.lower() in name.lower() for k in self.BLOATWARE_KEYWORDS)
                is_critical = any(k.lower() in name.lower() for k in self.CRITICAL_KEYWORDS)
                
                app_info = {
                    "name": name,
                    "id": full_name, # Needed for removal
                    "version": item.get("Version", "Unknown"),
                    "publisher": item.get("Publisher", "Unknown"),
                    "is_bloatware": is_bloat,
                    "is_critical": is_critical
                }
                apps.append(app_info)
                
            # Sort: Bloatware first, then alphabetical
            apps.sort(key=lambda x: (not x["is_bloatware"], x["name"]))
            
            return apps
            
        except Exception as e:
            self.logger.error(f"Error listing apps: {e}")
            return []

    def remove_app(self, package_full_name: str) -> bool:
        """Removes a specific AppX package."""
        try:
            cmd = [
                "powershell", "-NoProfile", "-Command",
                f"Get-AppxPackage -PackageTypeFilter Main -Name '{package_full_name}' | Remove-AppxPackage -ErrorAction Stop"
            # Using Name search because removing by FullName sometimes requires specifics.
            # Actually Remove-AppxPackage accepts -Package param. 
            # Ideally: Remove-AppxPackage -Package 'PackageFullName'
            ]
            
            # Refined command usage
            cmd = [
                "powershell", "-NoProfile", "-Command",
                f"Remove-AppxPackage -Package '{package_full_name}'"
            ]
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
            
            if result.returncode == 0:
                return True
            else:
                self.logger.error(f"Failed to remove {package_full_name}: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Error removing app: {e}")
            return False
