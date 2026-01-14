import sys
import os
import winreg
from typing import Tuple

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.telemetry_blocker import TelemetryBlocker

def check_registry_value(path: str, name: str) -> Tuple[bool, str]:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            path,
            0,
            winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return True, str(value)
    except WindowsError as e:
        return False, str(e)

def main():
    print("Initializing TelemetryBlocker...")
    blocker = TelemetryBlocker()
    
    print("\n--- Current Status ---")
    items = blocker.get_telemetry_status()
    for item in items:
        status = "BLOCKED" if item.is_blocked else "ALLOWED"
        print(f"[{status}] {item.name}")

    print("\n--- Testing Block All ---")
    success, msg = blocker.block_all_telemetry()
    print(f"Block All Result: {success}")
    print(f"Message: {msg}")
    
    print("\n--- Verifying Registry Keys ---")
    for reg_key in blocker.TELEMETRY_REGISTRY_KEYS:
        exists, value = check_registry_value(reg_key["path"], reg_key["name"])
        expected = reg_key["blocked_value"]
        status = "MATCH" if exists and str(value) == str(expected) else "MISMATCH"
        print(f"Key: {reg_key['name']}")
        print(f"  Path: {reg_key['path']}")
        print(f"  Current Value: {value}")
        print(f"  Blocked Value: {expected}")
        print(f"  Status: {status}")
        print("-" * 20)

if __name__ == "__main__":
    main()
