from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QCheckBox, QPushButton, QSlider, QTabWidget, QWidget, QFileDialog, QMessageBox, QProgressBar, QTextEdit)
from PySide6.QtCore import Qt

class SettingsWindow(QDialog):
    def __init__(self, profile_manager, audio_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VoxLiao Settings")
        self.setFixedSize(650, 550)
        self.profile_manager = profile_manager
        self.audio_manager = audio_manager
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Audio Routing Tab
        routing_tab = QWidget()
        routing_layout = QVBoxLayout(routing_tab)
        
        routing_layout.addWidget(QLabel("<b>1. Physical Microphone Input</b> (Your real mic)"))
        self.mic_combo = QComboBox()
        self.mic_combo.addItem("default")
        for dev in self.audio_manager.get_input_devices():
            self.mic_combo.addItem(dev['name'])
        self.mic_combo.setCurrentText(self.profile_manager.settings.get('mic_device', 'default'))
        routing_layout.addWidget(self.mic_combo)

        routing_layout.addWidget(QLabel("<b>2. Local Monitoring Device</b> (Your headphones)"))
        self.monitor_combo = QComboBox()
        self.monitor_combo.addItem("default")
        for dev in self.audio_manager.get_output_devices():
            self.monitor_combo.addItem(dev['name'])
        self.monitor_combo.setCurrentText(self.profile_manager.settings.get('monitor_device', 'default'))
        routing_layout.addWidget(self.monitor_combo)

        routing_layout.addWidget(QLabel("<b>3. Voice Chat Output Device</b> (Virtual Audio Cable)"))
        self.vc_combo = QComboBox()
        self.vc_combo.addItem("none")
        for dev in self.audio_manager.get_output_devices():
            self.vc_combo.addItem(dev['name'])
        self.vc_combo.setCurrentText(self.profile_manager.settings.get('voice_chat_device', 'none'))
        routing_layout.addWidget(self.vc_combo)
        
        # Audio Meters
        meters_layout = QHBoxLayout()
        
        mic_layout = QVBoxLayout()
        mic_layout.addWidget(QLabel("Mic Level"))
        self.mic_meter = QProgressBar()
        self.mic_meter.setRange(0, 100)
        mic_layout.addWidget(self.mic_meter)
        meters_layout.addLayout(mic_layout)

        sb_layout = QVBoxLayout()
        sb_layout.addWidget(QLabel("Soundboard Level"))
        self.sb_meter = QProgressBar()
        self.sb_meter.setRange(0, 100)
        sb_layout.addWidget(self.sb_meter)
        meters_layout.addLayout(sb_layout)

        out_layout = QVBoxLayout()
        out_layout.addWidget(QLabel("Voice Chat Output"))
        self.out_meter = QProgressBar()
        self.out_meter.setRange(0, 100)
        out_layout.addWidget(self.out_meter)
        meters_layout.addLayout(out_layout)

        routing_layout.addLayout(meters_layout)

        guide_btn = QPushButton("How others hear your sounds (Setup Guide)")
        guide_btn.clicked.connect(self.show_guide)
        routing_layout.addWidget(guide_btn)
        
        diag_group_layout = QHBoxLayout()
        test_snd_btn = QPushButton("Play Test Sound")
        test_snd_btn.clicked.connect(lambda: self.audio_manager.play_sound(-1, "sound/boom.mp3", 100, "play_once"))
        stop_btn = QPushButton("Stop All")
        stop_btn.clicked.connect(self.audio_manager.stop_all)
        diag_btn = QPushButton("Run Full Diagnostic")
        diag_btn.clicked.connect(self.run_diagnostics)
        
        diag_group_layout.addWidget(test_snd_btn)
        diag_group_layout.addWidget(stop_btn)
        diag_group_layout.addWidget(diag_btn)
        
        routing_layout.addLayout(diag_group_layout)

        routing_layout.addStretch()
        tabs.addTab(routing_tab, "Audio Routing")
        
        # Connect signals for meters
        self.audio_manager.mic_level_changed.connect(lambda v: self.mic_meter.setValue(int(v*100)))
        self.audio_manager.sb_level_changed.connect(lambda v: self.sb_meter.setValue(int(v*100)))
        self.audio_manager.out_level_changed.connect(lambda v: self.out_meter.setValue(int(v*100)))

        # Volumes & Modes Tab
        vol_tab = QWidget()
        vol_layout = QVBoxLayout(vol_tab)
        
        vol_layout.addWidget(QLabel("Routing Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Both Local + Voice Chat", "Voice Chat Only", "Local Only"])
        self.mode_combo.setCurrentText(self.profile_manager.settings.get('routing_mode', 'Both Local + Voice Chat'))
        vol_layout.addWidget(self.mode_combo)

        vol_layout.addWidget(QLabel("Master Output Volume:"))
        self.master_vol = QSlider(Qt.Orientation.Horizontal)
        self.master_vol.setRange(0, 100)
        self.master_vol.setValue(self.profile_manager.settings.get('master_volume', 100))
        vol_layout.addWidget(self.master_vol)

        vol_layout.addWidget(QLabel("Microphone Volume:"))
        self.mic_vol = QSlider(Qt.Orientation.Horizontal)
        self.mic_vol.setRange(0, 100)
        self.mic_vol.setValue(self.profile_manager.settings.get('mic_volume', 100))
        vol_layout.addWidget(self.mic_vol)

        vol_layout.addWidget(QLabel("Soundboard Volume:"))
        self.sb_vol = QSlider(Qt.Orientation.Horizontal)
        self.sb_vol.setRange(0, 100)
        self.sb_vol.setValue(self.profile_manager.settings.get('sb_volume', 100))
        vol_layout.addWidget(self.sb_vol)

        self.limiter_check = QCheckBox("Enable Audio Limiter / Compressor")
        self.limiter_check.setChecked(self.profile_manager.settings.get('limiter', True))
        vol_layout.addWidget(self.limiter_check)

        self.mute_mic_check = QCheckBox("Mute Microphone")
        self.mute_mic_check.setChecked(self.profile_manager.settings.get('mute_mic', False))
        vol_layout.addWidget(self.mute_mic_check)
        
        self.mute_sb_check = QCheckBox("Mute Soundboard")
        self.mute_sb_check.setChecked(self.profile_manager.settings.get('mute_sb', False))
        vol_layout.addWidget(self.mute_sb_check)

        vol_layout.addStretch()
        tabs.addTab(vol_tab, "Volumes & Modes")
        
        # General Tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        self.start_min = QCheckBox("Start Minimized")
        self.start_min.setChecked(self.profile_manager.settings.get('start_minimized', False))
        general_layout.addWidget(self.start_min)
        
        self.close_tray = QCheckBox("Close to System Tray")
        self.close_tray.setChecked(self.profile_manager.settings.get('close_tray', True))
        general_layout.addWidget(self.close_tray)

        general_layout.addWidget(QLabel("Stop All Sounds Hotkey:"))
        from PySide6.QtWidgets import QLineEdit
        self.stop_all_input = QLineEdit(self.profile_manager.settings.get('stop_all_hotkey', ''))
        self.stop_all_input.setPlaceholderText("e.g. ctrl+alt+s")
        general_layout.addWidget(self.stop_all_input)
        
        general_layout.addStretch()
        tabs.addTab(general_tab, "General")

        # Data Tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        export_btn = QPushButton("Export Soundboard (.echodeck)")
        export_btn.clicked.connect(self.export_soundboard)
        data_layout.addWidget(export_btn)

        import_btn = QPushButton("Import Soundboard (.echodeck)")
        import_btn.clicked.connect(self.import_soundboard)
        data_layout.addWidget(import_btn)

        data_layout.addStretch()
        tabs.addTab(data_tab, "Data")

        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_text = (
            "<h2>VoxLiao</h2>"
            "<p>Offline Soundboard</p>"
            "<p>Version 1.0.0</p>"
            "<p><b>Created by Theme613</b></p>"
            "<p>Your sounds. Your voice. Done.</p>"
            "<br/>"
            "<p>VoxLiao is an independent project and is not affiliated with Discord, Riot Games, Valorant, Elgato, Stream Deck, VB-Audio, or any third-party platform.</p>"
        )
        about_label = QLabel(about_text)
        about_label.setWordWrap(True)
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(about_label)
        
        support_btn = QPushButton("☕ Support Theme613")
        support_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff813f; 
                color: white; 
                font-weight: bold; 
                padding: 10px; 
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff9b6a;
            }
        """)
        support_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        support_btn.clicked.connect(self.open_support)
        about_layout.addWidget(support_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        support_desc = QLabel("Optional support helps fund updates, bug fixes, and new features.")
        support_desc.setStyleSheet("color: #727a87; font-size: 11px;")
        support_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(support_desc)

        tabs.addTab(about_tab, "About")
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def open_support(self):
        import webbrowser
        SUPPORT_URL = "PASTE_YOUR_BUY_ME_A_COFFEE_OR_KO_FI_LINK_HERE"
        if SUPPORT_URL and not SUPPORT_URL.startswith("PASTE_YOUR_"):
            webbrowser.open(SUPPORT_URL)
        else:
            QMessageBox.information(self, "Support", "Support link has not been configured yet.")

    def show_guide(self):
        guide_text = """
Step 1: Install a compatible virtual audio cable separately.
Step 2: In VoxLiao, go to Settings > Audio Routing.
Step 3: Set 'Voice Chat Output Device' to the virtual cable playback/input device, for example: 'CABLE Input'.
Step 4: Set 'Physical Microphone Input' to your real microphone.
Step 5: In Discord, open: User Settings > Voice & Video.
Step 6: Under Input Device, choose the matching virtual cable recording/output device, for example: 'CABLE Output'.
Step 7: Use Discord's Mic Test and press a VoxLiao sound button.
Step 8: If Discord cuts off music or effects: Disable automatic input sensitivity, Noise Suppression, Echo Cancellation, and Automatic Gain Control.

Warning: Use headphones when possible. Using speakers can cause echo or feedback because the microphone may capture speaker output.
"""
        QMessageBox.information(self, "Audio Routing Guide", guide_text)

    def run_diagnostics(self):
        # Apply current settings to manager temporarily so it tests the right thing
        self.save_settings(close=False)
        success, msg = self.audio_manager.run_diagnostics()
        if success:
            QMessageBox.information(self, "Diagnostic Result", f"✅ Success:\n\n{msg}")
        else:
            QMessageBox.warning(self, "Diagnostic Result", f"❌ Issues Found:\n\n{msg}")

    def save_settings(self, close=True):
        self.profile_manager.settings['mic_device'] = self.mic_combo.currentText()
        self.profile_manager.settings['monitor_device'] = self.monitor_combo.currentText()
        self.profile_manager.settings['voice_chat_device'] = self.vc_combo.currentText()
        
        self.profile_manager.settings['routing_mode'] = self.mode_combo.currentText()
        self.profile_manager.settings['master_volume'] = self.master_vol.value()
        self.profile_manager.settings['mic_volume'] = self.mic_vol.value()
        self.profile_manager.settings['sb_volume'] = self.sb_vol.value()
        self.profile_manager.settings['limiter'] = self.limiter_check.isChecked()
        self.profile_manager.settings['mute_mic'] = self.mute_mic_check.isChecked()
        self.profile_manager.settings['mute_sb'] = self.mute_sb_check.isChecked()

        self.profile_manager.settings['start_minimized'] = self.start_min.isChecked()
        self.profile_manager.settings['close_tray'] = self.close_tray.isChecked()
        self.profile_manager.settings['stop_all_hotkey'] = self.stop_all_input.text()
        
        self.profile_manager.save_settings()
        self.audio_manager.update_audio_device()
        if close:
            self.accept()

    def export_soundboard(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Soundboard", "", "VoxLiao Files (*.voxliao)")
        if filepath:
            try:
                self.profile_manager.export_soundboard(filepath)
                QMessageBox.information(self, "Export Successful", "Soundboard exported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"Failed to export: {e}")

    def import_soundboard(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Soundboard", "", "VoxLiao Files (*.voxliao)")
        if filepath:
            reply = QMessageBox.question(self, 'Confirm Import', 
                                         'This will overwrite your current profiles. Are you sure?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.profile_manager.import_soundboard(filepath)
                    QMessageBox.information(self, "Import Successful", "Soundboard imported successfully! The app will now reload profiles.")
                    self.accept()
                except Exception as e:
                    QMessageBox.warning(self, "Import Failed", f"Failed to import: {e}")
