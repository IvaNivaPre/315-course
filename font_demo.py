import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

class FontDemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Font Demo")
        self.setGeometry(100, 100, 800, 800)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)
        
        # Main container
        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        
        # Modern font options
        font_samples = [
            {"name": "Open Sans", "size": 14},
            {"name": "Segoe UI", "size": 14},
            {"name": "Arial", "size": 14},
            {"name": "Helvetica", "size": 14},
            {"name": "Verdana", "size": 14},
            {"name": "Tahoma", "size": 14},
        ]
        
        # Add title
        title = QLabel("Modern Font Demo")
        title_font = QFont("Montserrat", 24, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 30px;")
        layout.addWidget(title)
        
        # Create font samples
        for sample in font_samples:
            # Font name header
            header = QLabel(sample["name"])
            header_font = QFont(sample["name"], 16, QFont.Weight.Bold)
            header.setFont(header_font)
            header.setStyleSheet("color: #3498db; margin-top: 20px; margin-bottom: 10px;")
            layout.addWidget(header)
            
            # Sample text
            sample_text = QLabel(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Nullam at diam euismod, tincidunt nisi at, efficitur nisl. "
                "Aenean vehicula, nisi id ultrices tincidunt, nisl nisl "
                "aliquam nisl, eget ultrices nisl nisl eget nisl."
            )
            sample_text.setWordWrap(True)
            sample_font = QFont(sample["name"], sample["size"])
            sample_text.setFont(sample_font)
            sample_text.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
            layout.addWidget(sample_text)
            
            # Divider
            divider = QWidget()
            divider.setFixedHeight(1)
            divider.setStyleSheet("background-color: #ecf0f1; margin: 10px 0;")
            layout.addWidget(divider)
        
        # Add note
        note = QLabel("Note: Font availability depends on your system. Missing fonts may appear as system default.")
        note_font = QFont("Open Sans", 10)
        note.setFont(note_font)
        note.setStyleSheet("color: #7f8c8d; font-style: italic; margin-top: 30px;")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(note)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set app-wide styles
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f9f9f9;
        }
        QLabel {
            padding: 5px;
        }
    """)
    
    window = FontDemoWindow()
    window.show()
    sys.exit(app.exec())
