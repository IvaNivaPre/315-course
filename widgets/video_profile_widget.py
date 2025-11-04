import os
from PyQt6.QtCore import Qt, QRectF, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QBitmap, QPainterPath, QPainter, QIcon, QCursor
from PyQt6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QColor, QTransform
from ui.video_profile_ui import Ui_Form
from help import create_rounded_pixmap
from db import Database
from widgets.confirmation_dialog import ConfirmationDialog


class VideoProfileWidget(QWidget, Ui_Form):
    userProfileRequested = pyqtSignal(int)  # Сигнал для открытия профиля пользователя
    
    def __init__(self, db: Database, video_id: int, user_id: int = None, parent=None):
        super().__init__(parent)
        
        self.db = db
        self.video_id = video_id
        self.user_id = user_id
        self.channel_id = None
        
        self.setupUi(self)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(130)

        self.like_icon = QIcon('icons/like.svg')
        self.liked_icon = QIcon('icons/liked.svg')

        horizontal_flip = QTransform().scale(1, -1)

        like_pixmap = self.like_icon.pixmap(QSize(51, 51))
        like_flipped_pixmap = like_pixmap.transformed(horizontal_flip, Qt.TransformationMode.SmoothTransformation)
        self.dislike_icon = QIcon(like_flipped_pixmap)

        liked_pixmap = self.liked_icon.pixmap(QSize(51, 51))
        liked_flipped_pixmap = liked_pixmap.transformed(horizontal_flip, Qt.TransformationMode.SmoothTransformation)
        self.disliked_icon = QIcon(liked_flipped_pixmap)
        
        self.pushButton.clicked.connect(self.on_subscribe_clicked)
        self.like_btn.clicked.connect(self.on_like_clicked)
        self.dislike_btn.clicked.connect(self.on_dislike_clicked)
        
        self.load_data()
        
    def load_data(self):
        if not self.video_id:
            return
        video_data = self.db.get_video_info(self.video_id)
        if not video_data:
            return
            
        profile_info = self.db.get_video_profile_info(self.video_id)
        if not profile_info:
            return
            
        username, title, _, _, views_count, upload_date, _, _ = video_data
        subscribers_count, likes_count, dislikes_count, pfp_path = profile_info
        
        self.channel_id = self.db.get_channel_id_by_video(self.video_id)
        
        self.title.setText(title)
        self.nickname.setText(username)
        # Делаем никнейм кликабельным
        self.nickname.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.nickname.mousePressEvent = lambda event: self.on_nickname_clicked()
        self.views.setText(f"{views_count} просмотров")
        self.date.setText(upload_date)
        self.subscribers.setText(f"{subscribers_count} подписчиков")
        self.likes_label.setText(str(likes_count))
        self.dislikes_label.setText(str(dislikes_count))
        
        if pfp_path and os.path.exists(pfp_path):
            pixmap = QPixmap(pfp_path)
            rounded = create_rounded_pixmap(pixmap, QSize(50, 50))
            self.pfp.setPixmap(rounded)
        else:
            placeholder = QPixmap(50, 50)
            placeholder.fill(QColor("#ccc"))
            rounded_placeholder = create_rounded_pixmap(placeholder, QSize(50, 50))
            self.pfp.setPixmap(rounded_placeholder)

        self.load_user_status()
        self.setup_like_dislike_buttons()
    
    def load_user_status(self):
        if not self.user_id or not self.channel_id:
            self.is_liked = False
            self.is_disliked = False
            self.is_subscribed = False
            self.pushButton.hide()
            return
        
        if self.user_id == self.channel_id:
            self.pushButton.hide()
            self.is_subscribed = False
        else:
            self.pushButton.show()
            self.is_subscribed = self.db.is_subscribed(self.user_id, self.channel_id)
            if self.is_subscribed:
                self.pushButton.setText("Отписаться")
                self.pushButton.setStyleSheet(
                    "background: #E0E0E0;"
                    "border: 1px solid #ccc;"
                    "border-radius: 15px;"
                    "color: #606060;"
                )
            else:
                self.pushButton.setText("Subscribe")
                self.pushButton.setStyleSheet(
                    "background: #FF6D6D;"
                    "border: 1px solid #ccc;"
                    "border-radius: 15px;"
                    "color: white;"
                )
        
        like_status = self.db.get_user_like_status(self.user_id, self.video_id)
        self.is_liked = like_status is True
        self.is_disliked = like_status is False
    
    def setup_like_dislike_buttons(self):
        self.like_btn.setIcon(self.like_icon)
        self.dislike_btn.setIcon(self.dislike_icon)
        self._update_button_styles()
        self.like_btn.setStyleSheet("background: transparent;")
        self.dislike_btn.setStyleSheet("background: transparent;")
    
    def on_subscribe_clicked(self):
        if not self.user_id:
            ConfirmationDialog.show_information(self, "Авторизация", "Авторизуйтесь, чтобы подписаться на канал")
            return
        
        if not self.channel_id:
            return
        
        if self.is_subscribed:
            self.db.unsubscribe(self.user_id, self.channel_id)
            self.is_subscribed = False
            self.pushButton.setText("Subscribe")
            self.pushButton.setStyleSheet(
                "background: #FF6D6D;"
                "border: 1px solid #ccc;"
                "border-radius: 15px;"
                "color: white;"
            )
            current_subs = int(self.subscribers.text().split()[0])
            self.subscribers.setText(f"{max(0, current_subs - 1)} подписчиков")
        else:
            self.db.subscribe(self.user_id, self.channel_id)
            self.is_subscribed = True
            self.pushButton.setText("Отписаться")
            self.pushButton.setStyleSheet(
                "background: #E0E0E0;"
                "border: 1px solid #ccc;"
                "border-radius: 15px;"
                "color: #606060;"
            )
            current_subs = int(self.subscribers.text().split()[0])
            self.subscribers.setText(f"{current_subs + 1} подписчиков")
            
            # Обновляем предпочтения при подписке
            self.db.update_preference_on_subscribe(self.user_id, self.channel_id)
    
    def _update_button_styles(self):
        if self.is_liked:
            self.like_btn.setIcon(self.liked_icon)
            self.like_btn.setIconSize(QSize(30, 30))
        else:
            self.like_btn.setIcon(self.like_icon)
            self.like_btn.setIconSize(QSize(30, 30))
        
        if self.is_disliked:
            self.dislike_btn.setIcon(self.disliked_icon)
            self.dislike_btn.setIconSize(QSize(30, 30))
        else:
            self.dislike_btn.setIcon(self.dislike_icon)
            self.dislike_btn.setIconSize(QSize(30, 30))
    
    def on_like_clicked(self):
        if not self.user_id:
            ConfirmationDialog.show_information(self, "Авторизация", "Авторизуйтесь, чтобы оценить видео")
            return
        
        if self.is_liked:
            self.db.remove_like(self.user_id, self.video_id)
            self.is_liked = False
            current_likes = int(self.likes_label.text())
            self.likes_label.setText(str(max(0, current_likes - 1)))
        else:
            if self.is_disliked:
                current_dislikes = int(self.dislikes_label.text())
                self.dislikes_label.setText(str(max(0, current_dislikes - 1)))
                self.is_disliked = False
            
            self.db.set_like(self.user_id, self.video_id, is_like=True)
            self.is_liked = True
            current_likes = int(self.likes_label.text())
            self.likes_label.setText(str(current_likes + 1))
            
            # Обновляем предпочтения при лайке
            self.db.update_preference_on_like(self.user_id, self.video_id, is_like=True)
        
        self._update_button_styles()
    
    def on_dislike_clicked(self):
        if not self.user_id:
            ConfirmationDialog.show_information(self, "Авторизация", "Авторизуйтесь, чтобы оценить видео")
            return
        
        if self.is_disliked:
            self.db.remove_like(self.user_id, self.video_id)
            self.is_disliked = False
            current_dislikes = int(self.dislikes_label.text())
            self.dislikes_label.setText(str(max(0, current_dislikes - 1)))
        else:
            if self.is_liked:
                current_likes = int(self.likes_label.text())
                self.likes_label.setText(str(max(0, current_likes - 1)))
                self.is_liked = False
            
            self.db.set_like(self.user_id, self.video_id, is_like=False)
            self.is_disliked = True
            current_dislikes = int(self.dislikes_label.text())
            self.dislikes_label.setText(str(current_dislikes + 1))
            
            # Обновляем предпочтения при дизлайке
            self.db.update_preference_on_like(self.user_id, self.video_id, is_like=False)
        
        self._update_button_styles()
    
    def set_video_id(self, video_id):
        self.video_id = video_id
        self.load_data()
    
    def on_nickname_clicked(self):
        """Обработка клика по никнейму"""
        if self.channel_id:
            self.userProfileRequested.emit(self.channel_id)
    
    def set_user_id(self, user_id):
        """Обновляет user_id"""
        self.user_id = user_id
        self.load_user_status()
        self._update_button_styles()
