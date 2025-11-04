# test_video_profile.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from widgets.video_profile_widget import VideoProfileWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Video Profile")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Тестовый виджет профиля
        video_profile = VideoProfileWidget(
            title="Тестовое видео",
            author="Тестовый автор",
            views=15000,
            date="15 дек. 2024 г.",
            subscribers=125000,
            likes=850,
            dislikes=15,
            pfp_path="pics/car.jpg"  # Убедитесь что файл существует
        )
        
        layout.addWidget(video_profile)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())