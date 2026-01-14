import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    print("Verifying imports...")
    from src.modules.telemetry_blocker import TelemetryBlocker
    print("✓ TelemetryBlocker imported")
    from src.modules.permissions_manager import PermissionsManager
    print("✓ PermissionsManager imported")
    from src.modules.tracking_cleaner import TrackingCleaner
    print("✓ TrackingCleaner imported")
    from src.modules.firewall_manager import FirewallManager
    print("✓ FirewallManager imported")
    from src.ui.main_window import MainWindow
    print("✓ MainWindow imported")
    print("All imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
