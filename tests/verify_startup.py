import sys
import os
import winreg
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.profile_manager import ProfileManager

def verify_autostart():
    pm = ProfileManager()
    
    print("1. Checking initial state...")
    initial_state = pm.is_autostart_enabled()
    print(f"   Initial autostart enabled: {initial_state}")
    
    print("\n2. Enabling autostart...")
    success, msg = pm.enable_autostart()
    if not success:
        print(f"   FAILED to enable: {msg}")
        return
    print(f"   Result: {msg}")
    
    print("\n3. Verifying registry key...")
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            pm.AUTOSTART_KEY,
            0,
            winreg.KEY_READ
        )
        val, _ = winreg.QueryValueEx(key, pm.APP_NAME)
        winreg.CloseKey(key)
        print(f"   Registry Key Found: {val}")
        
        # Verify path correctness
        if "main.py" in val:
            print("   Path points to main.py (Correct for dev mode)")
        elif ".exe" in val:
            print("   Path points to .exe (Correct for frozen mode)")
        else:
            print("   WARNING: Path format unverified")
            
    except Exception as e:
        print(f"   FAILED to verify registry key: {e}")
        return

    print("\n4. Disabling autostart (cleanup)...")
    success, msg = pm.disable_autostart()
    if not success:
        print(f"   FAILED to disable: {msg}")
        return
    print(f"   Result: {msg}")
    
    print("\n5. Verifying removal...")
    enabled = pm.is_autostart_enabled()
    if not enabled:
        print("   Success: Registry key removed.")
    else:
        print("   FAILED: Registry key still exists.")

    # Restore initial state if it was enabled
    if initial_state:
        print("\n6. Restoring initial state (Enabled)...")
        pm.enable_autostart()

if __name__ == "__main__":
    verify_autostart()
