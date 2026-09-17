import sys
import webbrowser
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QStackedWidget, QWidget, QMessageBox)
from PySide6.QtCore import Qt

class SetupWizard(QDialog):
    def __init__(self, audio_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VoxLiao Audio Setup Wizard")
        self.setFixedSize(540, 380)
        
        self.audio_manager = audio_manager
        
        self.layout = QVBoxLayout(self)
        self.stack = QStackedWidget(self)
        self.layout.addWidget(self.stack)
        
        self.setup_pages()
        self.run_initial_scan()

    def setup_pages(self):
        # Page 1: Scanning
        self.page_scan = QWidget()
        scan_layout = QVBoxLayout(self.page_scan)
        scan_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scan_label = QLabel("Scanning for Virtual Audio Devices...")
        scan_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        scan_layout.addWidget(scan_label)
        self.stack.addWidget(self.page_scan)
        
        # Page 2: Missing Cable
        self.page_missing = QWidget()
        missing_layout = QVBoxLayout(self.page_missing)
        
        title_label = QLabel("<b>Virtual Audio Device Required</b>")
        title_label.setStyleSheet("font-size: 16px;")
        missing_layout.addWidget(title_label)
        
        if sys.platform == "darwin":
            desc_text = (
                "To let friends hear your VoxLiao sounds in Discord or game voice chat on macOS, "
                "you need a virtual audio driver.\n\n"
                "We recommend <b>BlackHole 2ch</b> (free & open-source, zero latency) or <b>VB-Cable for Mac</b>.\n\n"
                "<b>Quick Terminal Install:</b><br/><code>brew install blackhole-2ch</code><br/><br/>"
                "After installing, click <b>Scan Again</b> to automatically configure audio routing."
            )
        else:
            desc_text = (
                "To let friends hear your VoxLiao sounds in Discord or game voice chat, Windows needs a virtual audio cable.\n\n"
                "Because official drivers require administrator approval, VoxLiao cannot install it automatically.\n\n"
                "Click below to download VB-CABLE, install it, and then click <b>Scan Again</b>."
            )
            
        desc = QLabel(desc_text)
        desc.setWordWrap(True)
        desc.setTextFormat(Qt.TextFormat.RichText)
        missing_layout.addWidget(desc)
        
        btn_layout = QHBoxLayout()
        if sys.platform == "darwin":
            bh_btn = QPushButton("Download BlackHole (Free)")
            bh_btn.clicked.connect(lambda: webbrowser.open("https://github.com/ExistentialAudio/BlackHole"))
            vbc_btn = QPushButton("VB-Cable for Mac")
            vbc_btn.clicked.connect(lambda: webbrowser.open("https://vb-audio.com/Cable/"))
            btn_layout.addWidget(bh_btn)
            btn_layout.addWidget(vbc_btn)
        else:
            dl_btn = QPushButton("Download VB-CABLE")
            dl_btn.clicked.connect(lambda: webbrowser.open("https://vb-audio.com/Cable/"))
            btn_layout.addWidget(dl_btn)

        scan_btn = QPushButton("Scan Again")
        scan_btn.clicked.connect(self.run_initial_scan)
        btn_layout.addWidget(scan_btn)
        
        missing_layout.addStretch()
        missing_layout.addLayout(btn_layout)
        self.stack.addWidget(self.page_missing)
        
        # Page 3: Auto Configured
        self.page_success = QWidget()
        success_layout = QVBoxLayout(self.page_success)
        
        succ_title = QLabel("<b>Virtual Audio Device Detected!</b>")
        succ_title.setStyleSheet("color: #00d26a; font-size: 16px;")
        success_layout.addWidget(succ_title)
        
        succ_desc = QLabel("VoxLiao has automatically configured your audio routing:\n\n"
                           "• Selected your physical microphone\n"
                           "• Selected your local monitoring headphones\n"
                           "• Routed your microphone + soundboard mix to the virtual audio device\n\n"
                           "Click Next to complete the one-time Discord configuration.")
        succ_desc.setWordWrap(True)
        success_layout.addWidget(succ_desc)
        
        next_btn = QPushButton("Next")
        next_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_discord))
        success_layout.addStretch()
        success_layout.addWidget(next_btn)
        self.stack.addWidget(self.page_success)
        
        # Page 4: Discord Setup
        self.page_discord = QWidget()
        discord_layout = QVBoxLayout(self.page_discord)
        
        disc_title = QLabel("<b>Final Discord Setup Required</b>")
        disc_title.setStyleSheet("font-size: 16px;")
        discord_layout.addWidget(disc_title)
        
        device_example = "<b>BlackHole 2ch</b> (or CABLE Output)" if sys.platform == "darwin" else "<b>CABLE Output</b>"
        disc_text = (
            "VoxLiao mixes your microphone and sound effects together. "
            "To send this combined mix into Discord, set your Discord Input Device:\n\n"
            f"<b>Select {device_example} as Discord's Microphone Input.</b>\n\n"
            "Discord Steps:\n"
            "1. User Settings → Voice & Video\n"
            f"2. Input Device → Choose {device_example}\n"
            "3. Output Device → Keep set to your headphones\n"
            "4. Disable 'Noise Suppression' (Krisp) in Discord if sounds sound muffled."
        )
        disc_desc = QLabel(disc_text)
        disc_desc.setTextFormat(Qt.TextFormat.RichText)
        disc_desc.setWordWrap(True)
        discord_layout.addWidget(disc_desc)
        
        done_btn = QPushButton("Complete Setup")
        done_btn.clicked.connect(self.accept)
        discord_layout.addStretch()
        discord_layout.addWidget(done_btn)
        self.stack.addWidget(self.page_discord)

    def run_initial_scan(self):
        self.stack.setCurrentWidget(self.page_scan)
        if self.audio_manager.detect_virtual_cable():
            self.audio_manager.auto_select_devices()
            self.stack.setCurrentWidget(self.page_success)
        else:
            self.stack.setCurrentWidget(self.page_missing)
