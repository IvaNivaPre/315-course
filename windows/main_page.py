# main_page.py
from PyQt6.QtCore import pyqtSignal
from widgets.video_container_widget import VideoContainer
from windows.base_page import BasePage
from db import Database

class MainPage(BasePage):
    openVideoRequested = pyqtSignal(int)  # Сигнал для открытия видео
    
    def __init__(self, db: Database, user_id: int = None):
        self.db = db
        self.user_id = user_id
        super().__init__(page='main')

    def create_content_widget(self):
        self.video_container = VideoContainer(self.db, self.user_id)
        self.video_container.videoClicked.connect(self.openVideoRequested.emit)  # Пробрасываем сигнал
        self.video_container.add_video_widgets()
        return self.video_container
    
    def refresh(self):
        self.video_container.refresh()
    
    def set_user_id(self, user_id: int):
        """Обновляет user_id для персонализированных рекомендаций"""
        self.user_id = user_id
        self.video_container.set_user_id(user_id)
        self.video_container.refresh()
    
    def handle_search(self, query: str):
        """Обрабатывает поисковый запрос"""
        self.video_container.search(query)