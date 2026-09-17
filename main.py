import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush, QPen
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from core.profile_manager import resource_path

def create_fallback_icon():
    """ Creates a sleek 64x64 soundboard icon if no icon.png exists """
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Rounded dark chassis
    painter.setBrush(QBrush(QColor("#15171a")))
    painter.setPen(QPen(QColor("#2f343a"), 2))
    painter.drawRoundedRect(2, 2, 60, 60, 14, 14)
    
    # Soundboard key accents (green + cyan dots)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#00d26a")))
    painter.drawRoundedRect(10, 12, 18, 16, 4, 4)
    
    painter.setBrush(QBrush(QColor("#3b82f6")))
    painter.drawRoundedRect(36, 12, 18, 16, 4, 4)
    
    painter.setBrush(QBrush(QColor("#f43f5e")))
    painter.drawRoundedRect(10, 36, 18, 16, 4, 4)
    
    painter.setBrush(QBrush(QColor("#eab308")))
    painter.drawRoundedRect(36, 36, 18, 16, 4, 4)
    
    painter.end()
    return QIcon(pixmap)

def main():
    # Set up application
    app = QApplication(sys.argv)
    app.setApplicationName("VoxLiao")
    app.setOrganizationName("Theme613")
    
    # On macOS, prevent premature exit when windows are closed to tray
    app.setQuitOnLastWindowClosed(False)
    
    # Set app icon
    icon_path = resource_path("icon.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
    else:
        app_icon = create_fallback_icon()
    app.setWindowIcon(app_icon)
        
    window = MainWindow()
    
    # Clean shutdown hook
    def on_exit():
        try:
            window.hotkey_manager.stop()
            window.audio_manager.stop_engine()
        except Exception:
            pass
    app.aboutToQuit.connect(on_exit)
    
    # System Tray
    tray_icon = QSystemTrayIcon(app)
    tray_icon.setIcon(app_icon)
    tray_icon.setToolTip("VoxLiao Soundboard")
        
    tray_menu = QMenu()
    show_action = tray_menu.addAction("Show Soundboard")
    show_action.triggered.connect(window.show)
    
    stop_action = tray_menu.addAction("Stop All Sounds")
    stop_action.triggered.connect(window.audio_manager.stop_all)
    
    tray_menu.addSeparator()
    
    exit_action = tray_menu.addAction("Quit VoxLiao")
    exit_action.triggered.connect(app.quit)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()
    
    tray_icon.activated.connect(
        lambda reason: window.show() if reason in (
            QSystemTrayIcon.ActivationReason.DoubleClick, 
            QSystemTrayIcon.ActivationReason.Trigger
        ) else None
    )
    
    if not window.profile_manager.settings.get('start_minimized', False):
        window.show()
        window.raise_()
        window.activateWindow()
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
