from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, 
                             QLabel, QTextEdit, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from widgets.video_player_widget import VideoPlayerWithControls
from widgets.video_profile_widget import VideoProfileWidget
from widgets.collapsible_section import CollapsibleSection
from widgets.comments_widget import CommentsWidget
from windows.base_page import BasePage
from db import Database


class VideoViewPage(BasePage):
    video_started = pyqtSignal()
    userProfileRequested = pyqtSignal(int)  # Сигнал для открытия профиля пользователя
    
    def __init__(self, db: Database, user_id: int = None, parent=None):
        self.db = db
        self.user_id = user_id
        super().__init__(page='video')
        
    def create_content_widget(self):
        content_widget = QWidget()

        content_widget.setStyleSheet("""
            QWidget {
                background: #fef7ff;
            }
        """)
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем скроллируемую область для всего контента
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f8e8e9;
                width: 9px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #D45B69;
                border-radius: 4px;
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
        """)
        
        # Главный контейнер для контента
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)
        
        # Видеоплеер
        self.video_player = VideoPlayerWithControls()
        self.video_player.setStyleSheet("background: transparent;")
        self.content_layout.addWidget(self.video_player, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Профиль видео
        self.video_profile = VideoProfileWidget(
            db=self.db, 
            video_id=0, 
            user_id=self.user_id
        )
        # Подключаем сигнал открытия профиля
        self.video_profile.userProfileRequested.connect(self.userProfileRequested.emit)
        self.content_layout.addWidget(self.video_profile)
        
        self.setup_description_section()
        
        self.comments_widget = CommentsWidget(db=self.db, video_id=None, user_id=self.user_id)
        self.content_layout.addWidget(self.comments_widget)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        return content_widget
    
    def setup_description_section(self):
        """Настраивает сворачиваемую секцию с описанием видео"""
        self.description_section = CollapsibleSection("Описание видео")
        
        # Используем QTextEdit с фиксированным размером
        self.description_content = QTextEdit()
        self.description_content.setReadOnly(True)
        self.description_content.setFixedHeight(150)
        self.description_content.setStyleSheet("""
            QTextEdit {
                font-family: 'Segoe UI';
                padding: 15px;
                font-size: 14px;
                color: #333;
                background: #f3ded4;
                border: none;
                border-radius: 20px;
            }
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
        """)
        
        self.description_section.set_content(self.description_content)
        self.content_layout.addWidget(self.description_section)
    
    def set_video_data(self, video_id, watch_duration=0):
        video_data = self.db.get_video_info(video_id)
        if video_data is None:
            return
        
        _, _, video_path, description, _, _, _, _ = video_data
        
        self.video_player.load_video(video_path)
        
        # Восстанавливаем время просмотра, если есть
        if watch_duration > 0:
            self.video_player.set_position(watch_duration)
        
        self.video_profile.set_video_id(video_id)
        
        self.description_content.setText(description)
        
        # Устанавливаем video_id в CommentsWidget
        self.comments_widget.set_video_id(video_id)
        
        # Очищаем поле ввода комментария
        self.comments_widget.clear_input()
        
        # Прокручиваем страницу наверх
        self.scroll_area.verticalScrollBar().setValue(0)
    
    def get_current_position(self):
        """Получает текущую позицию воспроизведения в секундах"""
        return self.video_player.get_position()
    
    
    def cleanup(self):
        """Очистка ресурсов при закрытии страницы"""
        self.video_player.cleanup()

    def set_user_id(self, user_id):
        """Обновляет user_id и передает его в виджеты"""
        self.user_id = user_id
        self.video_profile.set_user_id(user_id)
        self.comments_widget.set_user_id(user_id)
    
    def refresh(self):
        """
        Refresh the page content.
        """
        # Можно добавить логику обновления при необходимости
        pass
