import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    # Set up application
    app = QApplication(sys.argv)
    app.setApplicationName("EchoDeck")
    
    # We can create a simple icon later, for now we will just use default or empty
    # Try to set an app icon if available
    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    window = MainWindow()
    
    # System Tray
    tray_icon = QSystemTrayIcon(app)
    if os.path.exists(icon_path):
        tray_icon.setIcon(QIcon(icon_path))
    else:
        # Create a simple colored pixmap for tray if no icon
        from PySide6.QtGui import QPixmap, QColor
        pix = QPixmap(16, 16)
        pix.fill(QColor("#3b82f6"))
        tray_icon.setIcon(QIcon(pix))
        
    tray_menu = QMenu()
    show_action = tray_menu.addAction("Show Soundboard")
    show_action.triggered.connect(window.show)
    
    stop_action = tray_menu.addAction("Stop All Sounds")
    stop_action.triggered.connect(window.audio_manager.stop_all)
    
    tray_menu.addSeparator()
    
    exit_action = tray_menu.addAction("Exit")
    exit_action.triggered.connect(app.quit)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()
    
    tray_icon.activated.connect(lambda reason: window.show() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
    
    if not window.profile_manager.settings.get('start_minimized', False):
        window.show()
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
