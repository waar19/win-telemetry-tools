"""
Windows Privacy Dashboard
Entry point for the application.
"""

import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Fix imports by adding project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.main_window import MainWindow


def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    # Enable High DPI scaling
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    
    # Check for admin rights
    if not is_admin():
        from PyQt6.QtWidgets import QMessageBox
        from src.i18n import tr
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(tr("admin.title"))
        msg.setText(tr("admin.message"))
        msg.setInformativeText(tr("admin.description"))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    # Set application metadata
    app.setApplicationName("Windows Privacy Dashboard")
    app.setApplicationVersion("1.3.0")
    app.setOrganizationName("WinPrivacy")
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
