from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime, timedelta

from widgets.long_video_block_widget import LongVideoBlock
from windows.base_page import BasePage
from help import apply_scroll_style
from db import Database


class HistoryPage(BasePage):
    videoClicked = pyqtSignal(int, int)
    
    def __init__(self, db: Database, user_id: int = None, page='history'):
        self.db = db
        self.user_id = user_id
        super().__init__(page)

    def create_content_widget(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        apply_scroll_style(scroll_area)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent; border: none;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(30, 30, 30, 30)
        self.container_layout.setSpacing(30)

        # Заглушка для неавторизованных пользователей
        self.auth_required_label = QLabel("Войдите в аккаунт для отображения истории просмотров")
        self.auth_required_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.auth_required_label.setStyleSheet(
            """
            font-family: 'Segoe UI';
            font-size: 24px;
            color: #888888;
            border: none;
            background: transparent;
            padding: 50px;
            """
        )
        self.auth_required_label.hide()
        
        # Заглушка для пустой истории
        self.empty_label = QLabel("История отсутствует")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            """
            font-family: 'Segoe UI';
            font-size: 24px;
            color: #888888;
            border: none;
            background: transparent;
            padding: 50px;
            """
        )
        self.empty_label.hide()

        self.container_layout.addWidget(self.auth_required_label)
        self.container_layout.addWidget(self.empty_label)
        # Добавляем stretch в конец, чтобы блоки не распределялись равномерно
        self.container_layout.addStretch()
        scroll_area.setWidget(self.container)

        # Устанавливаем начальное состояние
        if not self.user_id:
            self.auth_required_label.show()
            self.empty_label.hide()
        else:
            self.auth_required_label.hide()
            self.empty_label.hide()  # Скрываем, покажем если история пустая

        self.load_history_data()

        return scroll_area

    def add_date_block(self, date: str, videos_data: list):
        # Скрываем обе заглушки когда есть данные
        if self.empty_label.isVisible():
            self.empty_label.hide()
        if self.auth_required_label.isVisible():
            self.auth_required_label.hide()

        date_block = LongVideoBlock(self.db, date, videos_data)
        date_block.videoClicked.connect(self.videoClicked.emit)
        # Добавляем блок перед stretch (в позицию count-1)
        insert_pos = max(0, self.container_layout.count() - 1)
        self.container_layout.insertWidget(insert_pos, date_block)

    def clear_history(self):
        # Удаляем все виджеты кроме заглушек и stretch
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget and widget != self.empty_label and widget != self.auth_required_label:
                    widget.deleteLater()
        
        # Показываем соответствующую заглушку
        if not self.user_id:
            self.auth_required_label.show()
            self.empty_label.hide()
        else:
            self.empty_label.show()
            self.auth_required_label.hide()

    def load_history_data(self):
        """Загружает реальную историю из БД"""
        if not self.user_id:
            self.auth_required_label.show()
            self.empty_label.hide()
            return
        
        history = self.db.get_user_history(self.user_id)
        if not history:
            self.empty_label.show()
            self.auth_required_label.hide()
            return
        
        # Группируем по датам
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        grouped = {
            "Today": [],
            "Yesterday": [],
            "Last Week": [],
            "Earlier": []
        }
        
        for row in history:
            video_id = row['video_id']
            watch_duration = row['watch_duration'] or 0
            watched_at = row['watched_at']
            
            # Преобразуем строку в datetime
            try:
                watched_date = datetime.strptime(watched_at.split()[0], '%Y-%m-%d').date()
            except:
                watched_date = today
            
            if watched_date == today:
                grouped["Today"].append((video_id, watch_duration))
            elif watched_date == yesterday:
                grouped["Yesterday"].append((video_id, watch_duration))
            elif watched_date >= week_ago:
                grouped["Last Week"].append((video_id, watch_duration))
            else:
                grouped["Earlier"].append((video_id, watch_duration))
        
        # Добавляем блоки с видео
        for date_label, videos in grouped.items():
            if videos:
                self.add_date_block(date_label, videos)

    def refresh(self):
        self.clear_history()
        self.load_history_data()
    
    def set_user_id(self, user_id: int):
        """Устанавливает ID пользователя и обновляет историю"""
        self.user_id = user_id
        self.refresh()
    
    def handle_search(self, query: str):
        """Обрабатывает поисковый запрос по истории просмотров"""
        self.clear_history()
        
        if not self.user_id:
            self.auth_required_label.show()
            self.empty_label.hide()
            return
        
        # Если запрос пустой, показываем всю историю
        if not query or not query.strip():
            self.load_history_data()
            return
        
        # Выполняем поиск
        history = self.db.search_user_history(self.user_id, query)
        if not history:
            self.empty_label.show()
            self.auth_required_label.hide()
            return
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        grouped = {
            "Today": [],
            "Yesterday": [],
            "Last Week": [],
            "Earlier": []
        }
        
        for row in history:
            video_id = row['video_id']
            watch_duration = row['watch_duration'] or 0
            watched_at = row['watched_at']
            
            # Преобразуем строку в datetime
            try:
                watched_date = datetime.strptime(watched_at.split()[0], '%Y-%m-%d').date()
            except:
                watched_date = today
            
            if watched_date == today:
                grouped["Today"].append((video_id, watch_duration))
            elif watched_date == yesterday:
                grouped["Yesterday"].append((video_id, watch_duration))
            elif watched_date >= week_ago:
                grouped["Last Week"].append((video_id, watch_duration))
            else:
                grouped["Earlier"].append((video_id, watch_duration))
        
        # Добавляем блоки с видео
        for date_label, videos in grouped.items():
            if videos:
                self.add_date_block(date_label, videos)
