# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-01-14

### Added
- **Internationalization (i18n)**: Multi-language support
  - English (en)
  - Spanish (es)
  - German (de)
- **Settings Panel**: New panel to configure application preferences
- **Language Switcher**: Automatic system locale detection with manual override

### Improved
- **Async Loading**: All panels now load data in background threads for smoother navigation
- **Sidebar Buttons**: Improved visual styling to look like actual buttons
- **Error Handling**: Silently ignores non-existent services and scheduled tasks

### Fixed
- Fixed module import path issues for development and bundled modes
- Fixed telemetry blocker warnings for non-existent Windows tasks

---

## [1.0.0] - 2026-01-13

### Added
- **Telemetry Blocker**: Module to block Windows telemetry via Registry, Services, and Scheduled Tasks.
- **Permissions Manager**: Control over app access to Camera, Microphone, and Location.
- **Tracking Cleaner**: Tools to clear Activity History and reset Advertising ID.
- **Firewall Manager**: Block specific Microsoft telemetry endpoints.
- **Privacy Dashboard**: Modern UI with dark theme and Privacy Score.
- **Global Actions**: "Block All" and "Clean All" quick actions.

### Technical
- Initial release using Python and PyQt6.
- Standalone executable support via PyInstaller.
- GitHub Actions workflow for automated releases.
