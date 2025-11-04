from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import Qt

from widgets.video_horizontal_widget import HorizontalVideo
from help import apply_scroll_style


class LikedVideos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_example_data()

    def setup_ui(self):
        self.setFixedSize(650, 659)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            '''
                background: #f8e8e9;
                border: 1px solid #ccc;
                border-radius: 20px;
            '''
        )
        self.setContentsMargins(1, 15, 0, 15)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title = QLabel("Liked videos")
        title.setStyleSheet(
            '''
                font-family: 'Segoe UI';
                font-size: 30px;
                border: none;
                background: transparent;
                padding-left: 5px;
            '''
        )

        layout.addWidget(title)

        # ScrollArea для горизонтальных видео
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        apply_scroll_style(self.scroll_area)

        # Контейнер для видео
        self.container = QWidget()
        self.container.setStyleSheet('border: none')
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(12, 15, 0, 15)
        self.container_layout.setSpacing(15)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

    def load_example_data(self):
        video_data = [
            ("Awesome Programming Tutorial", "CodeMaster", "15K views", "3 days ago"),
            ("Machine Learning Basics", "AI Enthusiast", "8.9K views", "1 week ago"),
            ("PyQt6 Crash Course", "GUIGuru", "12.5K views", "2 days ago"),
            ("Data Visualization", "DataSciPro", "7.6K views", "5 days ago"),
            ("Web Development 2024", "WebWizard", "23.1K views", "2 weeks ago"),
        ]

        for title, author, views, date in video_data:
            video_widget = HorizontalVideo(title, author, views, date, thumbnail_path='pics/car.jpg')
            self.container_layout.addWidget(video_widget)

    def add_video(self, title, author, views, date, thumbnail_path):
        video_widget = HorizontalVideo(title, author, views, date, thumbnail_path)
        self.container_layout.addWidget(video_widget)

    def clear_videos(self):
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def refresh(self):
        """
        Refresh the liked videos content
        """
        # Clear existing content
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        
        # Reload data
        self.load_example_data()
