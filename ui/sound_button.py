from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QMenu, QGraphicsDropShadowEffect, QPushButton
from PySide6.QtCore import Qt, Signal, QRectF, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QFont, QCursor, QPainter, QLinearGradient, QBrush, QPainterPath

class StreamKeyButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_colors = ["#14171c", "#14171c"] # Default empty
        self.is_empty = True
        self.setStyleSheet("QPushButton { border: none; background: transparent; }")
        
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def set_gradient(self, color1, color2, is_empty=False):
        self.bg_colors = [color1, color2]
        self.is_empty = is_empty
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Base background gradient
        if self.is_empty:
            painter.setBrush(QColor("#14171c"))
        else:
            grad = QLinearGradient(0, 0, rect.width(), rect.height())
            grad.setColorAt(0.0, QColor(self.bg_colors[0]))
            grad.setColorAt(1.0, QColor(self.bg_colors[1]))
            painter.setBrush(QBrush(grad))
            
        # Draw base
        if self.is_empty:
            painter.setPen(QColor(255, 255, 255, 30)) # dashed border illusion
        else:
            painter.setPen(QColor(255, 255, 255, 25))
            
        # Button shape
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 14, 14)
        painter.drawPath(path)
        
        # Glass Reflection (::before)
        if not self.is_empty:
            refl_rect = QRectF(0, 0, rect.width(), rect.height() * 0.5)
            refl_grad = QLinearGradient(0, 0, 0, refl_rect.height())
            refl_grad.setColorAt(0.0, QColor(255, 255, 255, 56)) # 0.22
            refl_grad.setColorAt(0.7, QColor(255, 255, 255, 7))  # 0.03
            refl_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
            
            refl_path = QPainterPath()
            refl_path.addRoundedRect(refl_rect, 13, 13)
            # Make bottom curve larger to match HTML "40px" radius
            
            painter.setBrush(QBrush(refl_grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(refl_path)

        super().paintEvent(event)

class SoundButton(QWidget):
    clicked = Signal(int)
    edit_requested = Signal(int)
    
    def __init__(self, button_id, parent=None):
        super().__init__(parent)
        self.button_id = button_id
        self.data = {}
        self.is_playing = False
        
        self.setFixedSize(100, 100) # Slightly scaled down from full browser to fit desktop app gracefully
        
        # Key Socket (Recessed bezel)
        self.setStyleSheet("""
            SoundButton {
                background: #090a0c;
                border-radius: 18px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        self.btn = StreamKeyButton(self)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.clicked.connect(self.on_click)
        
        # Context menu
        self.btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn.customContextMenuRequested.connect(self.show_context_menu)
        
        btn_layout = QVBoxLayout(self.btn)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Typography
        self.name_label = QLabel("+", self.btn)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("color: #3b424e; font-size: 26px; font-weight: 300; background: transparent;")
        
        btn_layout.addWidget(self.name_label)
        self.layout.addWidget(self.btn)
        
        # Press Animation (Tactile Physics)
        self.anim = QPropertyAnimation(self.btn, b"pos")
        self.anim.setDuration(80)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def on_click(self):
        # Animate button press sink
        self.anim.setStartValue(QPoint(4, 4))
        self.anim.setEndValue(QPoint(4, 6))
        self.anim.start()
        
        if not self.data.get('file'):
            self.edit_requested.emit(self.button_id)
        else:
            self.clicked.emit(self.button_id)

    def update_data(self, data):
        self.data = data
        name = data.get('name', '')
        
        if not data.get('file'):
            self.btn.set_gradient("#14171c", "#14171c", True)
            self.name_label.setText("+")
            self.name_label.setStyleSheet("color: #3b424e; font-size: 26px; font-weight: 300; background: transparent;")
        else:
            # Generate gradient from single color (approximate)
            base_color = data.get('color', '#1976d2')
            if base_color == '#ffffff': base_color = '#1976d2' # give a color if white
            
            # Simple dark mode mapping based on the provided CSS keys
            self.btn.set_gradient(base_color, "#000000", False)
            self.name_label.setText(name)
            self.name_label.setStyleSheet("""
                color: #ffffff; 
                font-size: 13px; 
                font-weight: 700; 
                letter-spacing: 0.5px;
                background: transparent;
            """)
            
            # Optional hotkey overlay
            hotkey = data.get('hotkey', '')
            if hotkey:
                self.name_label.setText(f"{name}\n[{hotkey.upper()}]")

    def set_playing(self, playing):
        self.is_playing = playing
        # Maybe add a glow later
            
    def show_context_menu(self, pos):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit Button")
        
        action = menu.exec(self.btn.mapToGlobal(pos))
        if action == edit_action:
            self.edit_requested.emit(self.button_id)
