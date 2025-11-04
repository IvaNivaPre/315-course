from PyQt6.QtWidgets import QWidget, QGridLayout, QScrollArea
from PyQt6.QtCore import Qt

from widgets.video_tile_widget import VideoTileWidget
from db import Database
from PyQt6.QtCore import pyqtSignal


class VideoContainer(QScrollArea):
    videoClicked = pyqtSignal(int)

    def __init__(self, db: Database, user_id: int = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_id = user_id
        self.setup_ui()

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        # Контейнер для сетки видео
        self.container_widget = QWidget()
        self.videos_layout = QGridLayout(self.container_widget)
        self.videos_layout.setContentsMargins(17, 10, 17, 20)
        self.videos_layout.setHorizontalSpacing(17)
        self.videos_layout.setVerticalSpacing(20)

        self.setWidget(self.container_widget)
        self.apply_scrollbar_style()

    def apply_scrollbar_style(self):
        scrollbar_style = """
        QScrollBar:vertical {
            background: #f9e1d4;
            width: 6px;
            margin: 0px;
            border-radius: 3px;
        }

        QScrollBar::handle:vertical {
            background: #D45B69;
            border-radius: 3px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background: #c14a58;
        }

        QScrollBar::handle:vertical:pressed {
            background: #a83d49;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 0px;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        QScrollBar:horizontal {
            height: 0px;
        }
        """
        self.setStyleSheet(scrollbar_style)

    def add_video_widgets(self):
        # Используем систему рекомендаций
        video_ids = self.db.get_recommended_videos(user_id=self.user_id, limit=20)
        if video_ids:
            for idx, video_id in enumerate(video_ids):
                row = idx // 3
                col = idx % 3
                video_widget = VideoTileWidget(self.db, video_id)
                video_widget.videoClicked.connect(self.videoClicked.emit)
                self.videos_layout.addWidget(video_widget, row, col)

    def search(self, query: str):
        """Выполняет поиск видео и отображает результаты"""
        # Очищаем текущие виджеты
        while self.videos_layout.count():
            item = self.videos_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        
        # Если запрос пустой, показываем рекомендации
        if not query or not query.strip():
            self.add_video_widgets()
            return
        
        # Выполняем поиск
        video_ids = self.db.search_videos(query, limit=20)
        if video_ids:
            for i in range(len(video_ids)):
                row = i // 3
                col = i % 3
                video_widget = VideoTileWidget(self.db, video_ids[i])
                video_widget.videoClicked.connect(self.videoClicked.emit)
                self.videos_layout.addWidget(video_widget, row, col)

    def refresh(self):
        while self.videos_layout.count():
            item = self.videos_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        
        self.add_video_widgets()
    
    def set_user_id(self, user_id: int):
        """Обновляет user_id для персонализированных рекомендаций"""
        self.user_id = user_id
