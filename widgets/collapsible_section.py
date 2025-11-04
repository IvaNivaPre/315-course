from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QScrollArea
from PyQt6.QtGui import QIcon, QPixmap, QTransform
from help import apply_scroll_style

class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setup_ui(title)
        self.is_expanded = False
        self.content_height = 0
        
    def setup_ui(self, title):
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton {
                text-align: left;
                padding: 15px 20px;
                border: none;
                border-radius: 20px;
                background: #f8e8e9;
                font-family: 'Source Sans Pro';
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background: #eedfe0;
            }
            QFrame#contentFrame {
                background: #f8e8e9;
                border: none;
                border-radius: 20px;
                padding: 10px 20px 15px 20px;
            }
            QLabel {
                color: #333;
                font-family: 'Source Sans Pro';
                font-size: 14px;
                line-height: 1.4;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Load base icon
        self.base_icon = QIcon('icons/arrow_up.svg')
        
        self.header_btn = QPushButton(title)
        self.header_btn.setIcon(self.base_icon)  # Initial state: collapsed (down arrow)
        self.header_btn.clicked.connect(self.toggle)
        
        # Remove QFrame and QScrollArea
        self.content_widget = QWidget()
        self.content_widget.setVisible(False)
        
        # Create content layout directly
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        
        layout.addWidget(self.header_btn)
        layout.addWidget(self.content_widget)
        
        self.animation = QPropertyAnimation(self.content_widget, b"maximumHeight")
        self.animation.setDuration(400)  # Increased from 300 to 400 for even smoother animation
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuint)  # Corrected enum name

    def set_content(self, widget):
        # Remove existing content
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new widget directly
        self.content_layout.addWidget(widget)
        widget.adjustSize()
        self.content_height = widget.height()
        
    def toggle(self):
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.content_widget.setMaximumHeight(0)
            self.content_widget.setVisible(True)
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.content_height)
            self.flip_icon()
        else:
            self.animation.setStartValue(self.content_height)
            self.animation.setEndValue(0)
            self.flip_icon()
            
        self.animation.start()

    def flip_icon(self):
        pixmap = self.base_icon.pixmap(QSize(16, 16))
        if not pixmap.isNull():
            transform = QTransform().rotate(180 if self.is_expanded else 0)
            flipped_pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            self.header_btn.setIcon(QIcon(flipped_pixmap))
        else:
            self.header_btn.setIcon(self.base_icon)
