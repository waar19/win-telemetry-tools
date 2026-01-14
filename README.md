# Windows Privacy Dashboard

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🛡️ **All-in-one privacy management tool for Windows 11**

## Features

- **Telemetry Blocking** - Disable Windows telemetry services, scheduled tasks, and registry settings
- **App Permissions** - Manage camera, microphone, and location access for apps
- **App Cleaner** - Remove bloatware safely with protection for critical system apps
- **Tracking Cleanup** - Clear activity history, prefetch, timeline data, and reset Advertising ID
- **Browser Privacy** - Clean cache, cookies, and history for Chrome, Edge, and Firefox
- **Firewall Rules** - Block Microsoft telemetry endpoints at the network level
- **Network Monitor** - Real-time analysis of active connections and traffic
- **Update Control** - Manage Windows Update policies (Disable, Notify Only)
- **Privacy Profiles** - Export/Import settings and configure Auto-Start
- **Privacy Score** - Visual dashboard showing your overall privacy status
- **Multi-language** - Support for English, Spanish, and German

## Screenshots

*Coming soon*

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/brako718/win-telemetry-tools.git
cd win-telemetry-tools

# Install dependencies
pip install -r requirements.txt

# Run the application (as Administrator)
python src/main.py
```

### Standalone Executable

Download the latest `PrivacyDashboard.exe` from [Releases](https://github.com/brako718/win-telemetry-tools/releases).

> ⚠️ **Note**: Run as Administrator for full functionality.

## Building the Executable

```bash
pip install pyinstaller
pyinstaller privacy_dashboard.spec
```

The executable will be created in the `dist/` folder.

## Requirements

- Windows 10/11
- Python 3.10+
- Administrator privileges (for system modifications)

## License

MIT License - See [LICENSE](LICENSE) for details.

## Disclaimer

This tool modifies system settings. Use at your own risk. It is recommended to create a system restore point before making changes.
