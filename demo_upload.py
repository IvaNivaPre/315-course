# demo_upload.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from widgets.upload_video_widget import VideoUploadWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Hosting Platform - Upload Demo")
        self.setFixedSize(700, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        central_widget.setStyleSheet("background: #f0f0f0;")
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Виджет загрузки видео
        self.upload_widget = VideoUploadWidget()
        layout.addWidget(self.upload_widget)


def main():
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль для всего приложения
    app.setStyleSheet("""
        QMainWindow {
            background: #f0f0f0;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()