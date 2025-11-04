from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from db import Database
from widgets.video_horizontal_long_widget import HorizontalVideoLong


class LongVideoBlock(QWidget):
    videoClicked = pyqtSignal(int, int)
    
    def __init__(self, db: Database, heading: str, videos_data: list, parent=None):
        super().__init__(parent)
        self.db = db
        self.date = heading
        self.videos_data = videos_data
        self.setup_ui()

    def setup_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            '''
            background: #f8e8e9;
            border: 1px solid #ccc;
            border-radius: 20px;
            '''
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # Заголовок с датой
        title = QLabel(self.date)
        title.setStyleSheet(
            """
            font-family: 'Liberation Mono';
            font-size: 24px;
            font-weight: bold;
            color: #D45B69;
            border: none;
            background: transparent;
            padding: 0px;
        """
        )
        layout.addWidget(title)

        # Контейнер для видео
        self.videos_container = QWidget()
        self.videos_container.setStyleSheet('background: transparent; border: none;')
        self.videos_layout = QVBoxLayout(self.videos_container)
        self.videos_layout.setContentsMargins(0, 0, 0, 0)
        self.videos_layout.setSpacing(12)

        # Добавляем видео (без возможности удаления в истории)
        for video_data in self.videos_data:
            video_widget = HorizontalVideoLong(self.db, *video_data, can_delete=False)
            video_widget.videoClicked.connect(self.videoClicked.emit)
            self.videos_layout.addWidget(video_widget)
        
        # Добавляем stretch в конец, чтобы видео не распределялись равномерно
        self.videos_layout.addStretch()

        layout.addWidget(self.videos_container)

        self.adjustSize()
