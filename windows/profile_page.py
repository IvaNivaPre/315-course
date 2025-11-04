from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QStackedWidget, QPushButton, QDialog, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

from widgets.confirmation_dialog import ConfirmationDialog
from windows.base_page import BasePage
from widgets.profile_info_widget import ProfileInfo
from widgets.liked_videos_widget import LikedVideos
from widgets.subscriptions_widget import Subscriptions
from widgets.profile_videos_widget import ProfileVideos
from widgets.auth_widget import AuthWidget
from widgets.unauthenticated_profile_widget import UnauthenticatedProfileWidget
from help import apply_scroll_style
from db import Database


class ProfilePage(BasePage):
    loggedIn = pyqtSignal(int)  # Signal emitted when user logs in
    loggedOut = pyqtSignal()    # Signal emitted when user logs out
    
    def __init__(self, db: Database, user_id):
        self.db = db
        self.user_id = user_id  # ID авторизованного пользователя
        self.viewed_user_id = user_id  # ID просматриваемого профиля (по умолчанию свой)
        super().__init__('profile')
        
        # Create stacked widget for auth/profile states
        self.stacked = QStackedWidget()
        
        # Create unauthenticated profile widget
        self.unauthenticated_widget = UnauthenticatedProfileWidget()
        self.stacked.addWidget(self.unauthenticated_widget)
        
        # Connect login request signal
        self.unauthenticated_widget.loginRequested.connect(self.show_auth_dialog)
        
        # Create empty profile content (will be populated when authenticated)
        self.profile_content = QWidget()
        self.stacked.addWidget(self.profile_content)
        
        # Set initial state
        if self.user_id:
            self.show_profile()
        else:
            self.stacked.setCurrentIndex(0)
        
        self.layout().addWidget(self.stacked)
    
    def set_user_id(self, user_id):
        """Устанавливает ID авторизованного пользователя"""
        self.user_id = user_id
        self.viewed_user_id = user_id  # По умолчанию показываем свой профиль
        if user_id:
            self.show_profile()
        else:
            self.stacked.setCurrentIndex(0)
    
    def view_user_profile(self, user_id):
        """Открывает профиль конкретного пользователя"""
        if self.user_id is None:
            ConfirmationDialog.show_information(self, "Ошибка", "Авторизуйтесь для просмотра чужих профилей")
            return
        self.viewed_user_id = user_id
        self.show_profile()
    
    def view_my_profile(self):
        """Возвращает к своему профилю"""
        if self.user_id:
            self.viewed_user_id = self.user_id
            self.show_profile()
    
    def show_profile(self):
        """Show profile content when authenticated or viewing another profile"""
        # Проверяем, что есть ID профиля для просмотра
        if not self.viewed_user_id:
            self.stacked.setCurrentIndex(0)
            return
            
        # Clear previous content
        if self.profile_content:
            self.profile_content.deleteLater()
            
        # Recreate profile content with current user_id
        self.profile_content = QWidget()
        self.setup_profile_content()
        
        # Replace the old profile content in stacked widget
        self.stacked.removeWidget(self.stacked.widget(1))
        self.stacked.addWidget(self.profile_content)
        self.stacked.setCurrentIndex(1)

    def setup_profile_content(self):
        # Создаем ScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        apply_scroll_style(scroll_area)

        # Создаем основной контентный виджет
        profile_content = QWidget()
        main_layout = QVBoxLayout(profile_content)
        main_layout.setContentsMargins(35, 20, 35, 20)
        main_layout.setSpacing(30)

        # Определяем, просматриваем ли мы свой или чужой профиль
        is_own_profile = (self.user_id == self.viewed_user_id)
        
        # Добавляем информацию профиля
        self.profile_info = ProfileInfo(self.db, self.viewed_user_id, 
                                       current_user_id=self.user_id,
                                       is_own_profile=is_own_profile)
        # Подключаем сигнал выхода из аккаунта (только для своего профиля)
        if is_own_profile:
            self.profile_info.logoutRequested.connect(self.handle_logout)
        main_layout.addWidget(self.profile_info)

        # Добавляем видео профиля
        self.profile_videos = ProfileVideos(self.db, self.viewed_user_id, 
                                           current_user_id=self.user_id,
                                           is_own_profile=is_own_profile)
        main_layout.addWidget(self.profile_videos)

        # Лайкнутые видео и подписки показываем только для своего профиля
        if is_own_profile:
            # Создаем горизонтальный макет для лайкнутых видео и подписок
            content_layout = QHBoxLayout()
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(30)

            # Левая часть - лайкнутые видео
            self.liked_videos = LikedVideos()
            content_layout.addWidget(self.liked_videos)

            # Правая часть - подписки
            self.subscriptions = Subscriptions()
            content_layout.addWidget(self.subscriptions)

            main_layout.addLayout(content_layout)

        # Устанавливаем контент в ScrollArea
        scroll_area.setWidget(profile_content)

        # Создаем layout для profile_content и добавляем scroll_area
        layout = QVBoxLayout(self.profile_content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

    def handle_logout(self):
        """Handle logout request"""
        self.loggedOut.emit()

    def show_auth_dialog(self):
        """Shows authentication dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Login or Register")
        dialog.setFixedSize(520, 650)
        
        # Create auth widget
        auth_widget = AuthWidget(self.db)
        
        # Connect auth signals
        auth_widget.loggedIn.connect(lambda user_id: dialog.accept())
        auth_widget.loggedIn.connect(self.loggedIn.emit)
        
        # Set dialog layout
        layout = QVBoxLayout(dialog)
        layout.addWidget(auth_widget)
        dialog.exec()

    def update_profile_info(self, nickname, subscribers_count):
        """Обновляет информацию профиля"""
        self.profile_info.nickname.setText(nickname)
        self.profile_info.subscribers.setText(f"{subscribers_count} подписчиков")

    def add_liked_video(self, title, author, views, date):
        """Добавляет видео в лайкнутые"""
        if hasattr(self, 'liked_videos'):
            self.liked_videos.add_video(title, author, views, date)

    def add_subscription(self, username):
        """Добавляет подписку"""
        if hasattr(self, 'subscriptions'):
            self.subscriptions.add_subscription(username)

    def clear_all_content(self):
        """Очищает весь контент"""
        if hasattr(self, 'liked_videos'):
            self.liked_videos.clear_videos()
        if hasattr(self, 'subscriptions'):
            self.subscriptions.clear_subscriptions()
    
    def refresh(self):  
        if self.user_id:
            self.show_profile()
