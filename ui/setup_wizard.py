import webbrowser
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QStackedWidget, QWidget, QMessageBox)
from PySide6.QtCore import Qt

class SetupWizard(QDialog):
    def __init__(self, audio_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VoxLiao Audio Setup")
        self.setFixedSize(500, 350)
        
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
        scan_layout.addWidget(QLabel("Scanning for Virtual Audio Cable..."))
        self.stack.addWidget(self.page_scan)
        
        # Page 2: Missing Cable
        self.page_missing = QWidget()
        missing_layout = QVBoxLayout(self.page_missing)
        
        title_label = QLabel("<b>Virtual Audio Cable Required</b>")
        title_label.setStyleSheet("font-size: 16px;")
        missing_layout.addWidget(title_label)
        
        desc = QLabel("To let friends hear your VoxLiao sounds in Discord or game voice chat, Windows needs a virtual audio cable.\n\n"
                      "Because the official VB-CABLE driver requires Windows administrator approval, VoxLiao cannot legally install it for you automatically.\n\n"
                      "Click below to download it from the official VB-Audio website, install it, and then click Scan Again.")
        desc.setWordWrap(True)
        missing_layout.addWidget(desc)
        
        btn_layout = QHBoxLayout()
        dl_btn = QPushButton("Download and Install VB-CABLE")
        dl_btn.clicked.connect(self.open_vbcable_website)
        scan_btn = QPushButton("Scan Again")
        scan_btn.clicked.connect(self.run_initial_scan)
        
        btn_layout.addWidget(dl_btn)
        btn_layout.addWidget(scan_btn)
        
        missing_layout.addStretch()
        missing_layout.addLayout(btn_layout)
        self.stack.addWidget(self.page_missing)
        
        # Page 3: Auto Configured
        self.page_success = QWidget()
        success_layout = QVBoxLayout(self.page_success)
        
        succ_title = QLabel("<b>Virtual Audio Cable Detected!</b>")
        succ_title.setStyleSheet("color: #00d26a; font-size: 16px;")
        success_layout.addWidget(succ_title)
        
        succ_desc = QLabel("VoxLiao has automatically configured your routing:\n\n"
                           "- Selected your physical microphone\n"
                           "- Selected your local monitoring headphones\n"
                           "- Routed the mix into CABLE Input\n\n"
                           "Voice-chat routing is active. VoxLiao is sending microphone and soundboard audio to CABLE Input.")
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
        
        disc_desc = QLabel("VoxLiao automatically configures its own microphone and sound routing. Discord and some games require one final manual choice:\n\n"
                           "<b>Select CABLE Output as the app's microphone input.</b>\n\n"
                           "Discord path:\n"
                           "User Settings → Voice & Video → Input Device → CABLE Output")
        disc_desc.setWordWrap(True)
        discord_layout.addWidget(disc_desc)
        
        done_btn = QPushButton("I Have Selected CABLE Output (Finish)")
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
            
    def open_vbcable_website(self):
        webbrowser.open("https://vb-audio.com/Cable/")
