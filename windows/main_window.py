from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import QTimer
from windows.main_page import MainPage
from windows.history_page import HistoryPage
from windows.profile_page import ProfilePage
from windows.video_view_page import VideoViewPage
from db import Database

class MainWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.current_user_id = None
        self.setWindowTitle("Video Platform")
        self.setFixedSize(1201, 897)

        # Создаем stacked widget для управления страницами
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создаем страницы
        self.main_page = MainPage(db, self.current_user_id)
        self.history_page = HistoryPage(db, self.current_user_id)
        self.profile_page = ProfilePage(db, self.current_user_id)
        self.video_view_page = VideoViewPage(db, self.current_user_id)

        # Добавляем страницы в stacked widget
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.history_page)
        self.stacked_widget.addWidget(self.profile_page)
        self.stacked_widget.addWidget(self.video_view_page)

        # Подключаем сигналы
        self.main_page.menu_widget.pageChanged.connect(self.switch_page)
        self.history_page.menu_widget.pageChanged.connect(self.switch_page)
        self.profile_page.menu_widget.pageChanged.connect(self.switch_page)
        self.video_view_page.menu_widget.pageChanged.connect(self.switch_page)
        
        self.main_page.openVideoRequested.connect(lambda vid: self.open_video(vid, 0))
        self.history_page.videoClicked.connect(self.open_video)
        
        self.profile_page.loggedIn.connect(self.handle_login)
        self.profile_page.loggedOut.connect(self.handle_logout)
        
        self.video_view_page.userProfileRequested.connect(self.view_user_profile)
        
        # Таймер для засчитывания просмотра
        self.view_timer = QTimer()
        self.view_timer.setSingleShot(True)
        self.view_timer.timeout.connect(self.record_view)
        self.current_video_id = None

    def switch_page(self, page):
        # При уходе со страницы видео сохраняем время просмотра
        current_widget = self.stacked_widget.currentWidget()
        if current_widget == self.video_view_page and page != 'video':
            if self.current_video_id and self.current_user_id:
                current_position = self.video_view_page.get_current_position()
                # Проверяем на None и заменяем на 0
                if current_position is None:
                    current_position = 0
                self.db.add_to_watch_history(self.current_user_id, self.current_video_id, current_position)
            # Останавливаем таймер просмотра
            if self.view_timer.isActive():
                self.view_timer.stop()
        
        pages_indexes = {
            'main': 0,
            'history': 1,
            'profile': 2,
            'video': 3
        }
        if page in pages_indexes:
            if page == 'profile' and self.current_user_id:
                self.profile_page.view_my_profile()
            self.stacked_widget.setCurrentIndex(pages_indexes[page])
        
    def open_video(self, video_id, watch_duration=0):
        if self.view_timer.isActive():
            self.view_timer.stop()
        
        self.video_view_page.set_video_data(video_id, watch_duration)
        self.stacked_widget.setCurrentIndex(3)
        
        self.current_video_id = video_id
        
        if self.current_user_id:
            self.db.add_to_watch_history(self.current_user_id, video_id, watch_duration)
        
        self.view_timer.start(7000)
    
    def record_view(self):
        if self.current_video_id:
            self.db.increment_views(self.current_video_id)
            
            if self.current_user_id:
                self.db.update_preference_on_watch(self.current_user_id, self.current_video_id)

    def refresh_current_page(self):
        current_page = self.stacked_widget.currentWidget()
        current_page.refresh()

    def handle_login(self, user_id):
        self.current_user_id = user_id
        self.main_page.set_user_id(user_id)
        self.profile_page.set_user_id(user_id)
        self.history_page.set_user_id(user_id)
        self.video_view_page.set_user_id(user_id)

    def handle_logout(self):
        self.current_user_id = None
        self.main_page.set_user_id(None)
        self.profile_page.set_user_id(None)
        self.history_page.set_user_id(None)
        self.video_view_page.set_user_id(None)
    
    def view_user_profile(self, user_id):
        self.profile_page.view_user_profile(user_id)
        self.stacked_widget.setCurrentIndex(2)
