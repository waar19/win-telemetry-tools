"""
Browser Cleaner Module
Handles cleaning of browser data (Cache, Cookies, History).
"""

import os
import shutil
import glob
from dataclasses import dataclass
from typing import List, Tuple
from pathlib import Path

@dataclass
class BrowserItem:
    name: str
    browser: str
    paths: List[str]
    description: str

class BrowserCleaner:
    """Manages browser data cleaning."""
    
    def __init__(self):
        self.local_app_data = os.environ.get("LOCALAPPDATA")
        self.app_data = os.environ.get("APPDATA")
    
    def get_cleanable_items(self) -> List[BrowserItem]:
        """Scanning for supported browsers."""
        items = []
        
        # Google Chrome
        chrome_path = Path(self.local_app_data) / "Google" / "Chrome" / "User Data" / "Default"
        if chrome_path.exists():
            items.extend([
                BrowserItem("Chrome Cache", "Google Chrome", [str(chrome_path / "Cache"), str(chrome_path / "Code Cache")], "Temporary internet files"),
                BrowserItem("Chrome Cookies", "Google Chrome", [str(chrome_path / "Cookies"), str(chrome_path / "Cookies-journal")], "Tracking cookies"),
                BrowserItem("Chrome History", "Google Chrome", [str(chrome_path / "History"), str(chrome_path / "History-journal")], "Browsing history"),
            ])
            
        # Microsoft Edge
        edge_path = Path(self.local_app_data) / "Microsoft" / "Edge" / "User Data" / "Default"
        if edge_path.exists():
            items.extend([
                BrowserItem("Edge Cache", "Microsoft Edge", [str(edge_path / "Cache"), str(edge_path / "Code Cache")], "Temporary internet files"),
                BrowserItem("Edge Cookies", "Microsoft Edge", [str(edge_path / "Cookies")], "Tracking cookies"),
                BrowserItem("Edge History", "Microsoft Edge", [str(edge_path / "History")], "Browsing history"),
            ])
            
        # Firefox
        firefox_path = Path(self.app_data) / "Mozilla" / "Firefox" / "Profiles"
        if firefox_path.exists():
            for profile in firefox_path.glob("*.default-release"):
                items.extend([
                    BrowserItem("Firefox Cache", "Mozilla Firefox", [str(profile / "cache2")], "Temporary internet files"),
                    BrowserItem("Firefox Cookies", "Mozilla Firefox", [str(profile / "cookies.sqlite")], "Tracking cookies"),
                    BrowserItem("Firefox History", "Mozilla Firefox", [str(profile / "places.sqlite")], "Browsing history"),
                ])
        
        return items

    def clean_items(self, items: List[BrowserItem]) -> Tuple[bool, str, int]:
        """Clean selected browser items."""
        total_bytes = 0
        errors = []
        
        for item in items:
            for path_str in item.paths:
                path = Path(path_str)
                if not path.exists():
                    continue
                
                try:
                    if path.is_file():
                        size = path.stat().st_size
                        path.unlink()
                        total_bytes += size
                    elif path.is_dir():
                        size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                        shutil.rmtree(path)
                        total_bytes += size
                except Exception as e:
                    errors.append(f"Failed to clean {item.name}: {e}")
        
        if errors:
            return False, "\n".join(errors[:3]), total_bytes
        return True, "Browser cleanup complete", total_bytes
