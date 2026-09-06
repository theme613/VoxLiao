from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QComboBox, QFileDialog, QColorDialog, QSlider)
from PySide6.QtCore import Qt

class ButtonEditorDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Button")
        self.setFixedSize(400, 500)
        self.data = data.copy()
        
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Button Name:"))
        self.name_input = QLineEdit(self.data.get('name', ''))
        layout.addWidget(self.name_input)
        
        # File
        layout.addWidget(QLabel("Audio File:"))
        file_layout = QHBoxLayout()
        self.file_input = QLineEdit(self.data.get('file', ''))
        self.file_input.setReadOnly(True)
        file_layout.addWidget(self.file_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        # Hotkey
        layout.addWidget(QLabel("Hotkey:"))
        self.hotkey_input = QLineEdit(self.data.get('hotkey', ''))
        self.hotkey_input.setPlaceholderText("e.g. F1, ctrl+alt+a")
        layout.addWidget(self.hotkey_input)
        
        # Color
        color_layout = QHBoxLayout()
        self.color_btn = QPushButton("Change Background Color")
        self.color_btn.clicked.connect(self.pick_bg_color)
        color_layout.addWidget(self.color_btn)
        
        self.text_color_btn = QPushButton("Change Text Color")
        self.text_color_btn.clicked.connect(self.pick_text_color)
        color_layout.addWidget(self.text_color_btn)
        layout.addLayout(color_layout)
        
        # Volume
        layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 200)
        self.volume_slider.setValue(self.data.get('volume', 100))
        layout.addWidget(self.volume_slider)
        
        # Mode
        layout.addWidget(QLabel("Playback Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["play_once", "loop", "stop_previous"])
        self.mode_combo.setCurrentText(self.data.get('mode', 'play_once'))
        layout.addWidget(self.mode_combo)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.wav *.mp3 *.ogg *.flac)")
        if filepath:
            self.file_input.setText(filepath)
            
    def pick_bg_color(self):
        color = QColorDialog.getColor(initial=self.data.get('color', '#ffffff'), parent=self)
        if color.isValid():
            self.data['color'] = color.name()
            
    def pick_text_color(self):
        color = QColorDialog.getColor(initial=self.data.get('text_color', '#000000'), parent=self)
        if color.isValid():
            self.data['text_color'] = color.name()

    def get_data(self):
        self.data['name'] = self.name_input.text()
        self.data['file'] = self.file_input.text()
        self.data['hotkey'] = self.hotkey_input.text()
        self.data['volume'] = self.volume_slider.value()
        self.data['mode'] = self.mode_combo.currentText()
        return self.data
