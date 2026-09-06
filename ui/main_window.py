import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QGridLayout, QPushButton, QLabel, QSystemTrayIcon, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction, QColor

from ui.sound_button import SoundButton
from ui.button_editor import ButtonEditorDialog
from ui.settings_window import SettingsWindow
from ui.setup_wizard import SetupWizard
from core.profile_manager import ProfileManager
from core.audio_manager import AudioManager
from core.hotkey_manager import HotkeyManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoxLiao")
        self.setFixedSize(680, 520)
        
        # Match HTML body background color (simulated with a dark flat background, gradient chassis inside)
        self.setStyleSheet("QMainWindow { background-color: #1b1e24; }")

        self.profile_manager = ProfileManager()
        self.audio_manager = AudioManager(self.profile_manager)
        self.hotkey_manager = HotkeyManager(self.profile_manager)
        self.hotkey_manager.hotkey_triggered.connect(self.on_button_clicked)
        self.hotkey_manager.stop_all_triggered.connect(self.audio_manager.stop_all)

        self.current_profile_index = 0
        self.profile_names = ["Profile 1", "Profile 2", "Profile 3", "Profile 4", "Custom"]

        self.setup_ui()
        self.load_profile()
        self.setup_global_hotkeys()
        
        # Connect audio signals to update buttons
        self.audio_manager.playback_started.connect(self.on_playback_started)
        self.audio_manager.playback_stopped.connect(self.on_playback_stopped)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Chassis Frame (matches .streamdeck-chassis)
        self.chassis = QWidget()
        self.chassis.setStyleSheet("""
            QWidget#Chassis {
                background-color: #15171a;
                border-radius: 28px;
                border: 1px solid #2f343a;
            }
        """)
        self.chassis.setObjectName("Chassis")
        
        chassis_layout = QVBoxLayout(self.chassis)
        chassis_layout.setContentsMargins(28, 24, 28, 28)
        chassis_layout.setSpacing(20)

        # Top Bar
        top_bar = QHBoxLayout()
        
        # Brand Logo
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(8)
        
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet("background-color: #00d26a; border-radius: 4px;")
        
        brand_text = QLabel("STREAM DECK")
        brand_text.setStyleSheet("""
            color: #58606d;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        
        logo_layout.addWidget(dot)
        logo_layout.addWidget(brand_text)
        top_bar.addLayout(logo_layout)
        
        top_bar.addStretch()

        # Bank Switcher
        bank_container = QWidget()
        bank_container.setStyleSheet("""
            QWidget {
                background: #111316;
                border-radius: 10px;
                border: 1px solid #23272d;
            }
        """)
        bank_layout = QHBoxLayout(bank_container)
        bank_layout.setContentsMargins(3, 3, 3, 3)
        bank_layout.setSpacing(2)

        self.profile_buttons = []
        for i in range(5):
            btn = QPushButton(str(i + 1) if i < 4 else "Custom")
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Match .bank-btn styles in CSS
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #727a87;
                    font-size: 11px;
                    font-weight: 600;
                    padding: 5px 12px;
                    border-radius: 7px;
                }
                QPushButton:hover {
                    color: #dbe0e8;
                }
                QPushButton:checked {
                    background: #252a32;
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_profile(idx))
            self.profile_buttons.append(btn)
            bank_layout.addWidget(btn)
            
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setObjectName("settingsBtn")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: #111316;
                border: 1px solid #23272d;
                border-radius: 8px;
                color: #727a87;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #ffffff;
                border: 1px solid #3b424e;
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        self.setup_btn = QPushButton("⚡ Set Up Voice Chat Automatically")
        self.setup_btn.setObjectName("setupBtn")
        self.setup_btn.setFixedHeight(30)
        self.setup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setup_btn.setStyleSheet("""
            QPushButton {
                background: #00d26a;
                color: #000000;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 10px;
                border: none;
            }
            QPushButton:hover {
                background: #00e676;
            }
        """)
        self.setup_btn.clicked.connect(self.open_setup_wizard)
        
        top_bar.addWidget(bank_container)
        top_bar.addWidget(self.setup_btn)
        top_bar.addWidget(self.settings_btn)

        chassis_layout.addLayout(top_bar)

        # Grid Viewport (.bank-page)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(4, 4, 4, 4)
        self.grid_layout.setSpacing(16)
        
        self.buttons = []
        for i in range(10):
            btn = SoundButton(i)
            btn.clicked.connect(self.on_button_clicked)
            btn.edit_requested.connect(self.open_button_editor)
            self.buttons.append(btn)
            row, col = divmod(i, 5)
            self.grid_layout.addWidget(btn, row, col)

        chassis_layout.addWidget(self.grid_widget)
        main_layout.addWidget(self.chassis)
        
        footer = QLabel("Created by Theme613")
        footer.setStyleSheet("color: #58606d; font-size: 11px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)

    def switch_profile(self, index):
        for i, btn in enumerate(self.profile_buttons):
            btn.setChecked(i == index)
        self.current_profile_index = index
        self.load_profile()
        self.setup_global_hotkeys()

    def get_current_profile_data(self):
        name = self.profile_names[self.current_profile_index]
        profile = self.profile_manager.profiles.get(name, {})
        # Convert button array to dict mapping string ID to button data
        data_dict = {}
        for b in profile.get("buttons", []):
            data_dict[str(b["id"])] = b
        return data_dict

    def update_button_data(self, button_id, new_data):
        name = self.profile_names[self.current_profile_index]
        profile = self.profile_manager.profiles.get(name)
        if profile:
            for i, b in enumerate(profile["buttons"]):
                if b["id"] == button_id:
                    profile["buttons"][i] = new_data
                    break
            self.profile_manager.save_profile(profile)

    def load_profile(self):
        data = self.get_current_profile_data()
        for i, btn in enumerate(self.buttons):
            btn_data = data.get(str(i), {})
            btn.update_data(btn_data)

    def on_button_clicked(self, button_id):
        btn_data = self.get_current_profile_data().get(str(button_id), {})
        filepath = btn_data.get('file')
        if filepath:
            volume = btn_data.get('volume', 100)
            mode = btn_data.get('mode', 'play_once')
            self.audio_manager.play_sound(button_id, filepath, volume, mode)

    def open_button_editor(self, button_id):
        current_data = self.get_current_profile_data().get(str(button_id), {})
        dialog = ButtonEditorDialog(current_data, self)
        if dialog.exec():
            new_data = dialog.get_data()
            new_data["id"] = button_id
            self.update_button_data(button_id, new_data)
            self.load_profile()
            self.setup_global_hotkeys()

    def open_settings(self):
        dialog = SettingsWindow(self.profile_manager, self.audio_manager, self)
        if dialog.exec():
            self.setup_global_hotkeys()
            
    def open_setup_wizard(self):
        dialog = SetupWizard(self.audio_manager, self)
        dialog.exec()

    def setup_global_hotkeys(self):
        name = self.profile_names[self.current_profile_index]
        self.hotkey_manager.refresh_hotkeys(name)

    def on_playback_started(self, button_id):
        if 0 <= button_id < len(self.buttons):
            self.buttons[button_id].set_playing(True)

    def on_playback_stopped(self, button_id):
        if 0 <= button_id < len(self.buttons):
            self.buttons[button_id].set_playing(False)

    def closeEvent(self, event):
        if self.profile_manager.settings.get('close_tray', True):
            event.ignore()
            self.hide()
        else:
            self.audio_manager.stop_engine()
            event.accept()
