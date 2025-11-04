from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QScrollArea, QLabel, QHBoxLayout, QDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from widgets.video_horizontal_long_widget import HorizontalVideoLong
from widgets.upload_video_widget import VideoUploadWidget
from help import apply_scroll_style
from db import Database


class UploadDialog(QDialog):
    def __init__(self, db: Database, user_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_id = user_id
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Загрузить видео")
        self.setFixedSize(700, 700)
        
        # Устанавливаем стиль для диалога
        self.setStyleSheet("""
            QDialog {
                background: #f0f0f0;
            }
        """)
        
        # Главный layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Виджет загрузки видео
        self.upload_widget = VideoUploadWidget(self.db, self.user_id)
        main_layout.addWidget(self.upload_widget)


class ProfileVideos(QWidget):
    def __init__(self, db: Database, user_id, current_user_id=None, is_own_profile=True, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_id = user_id  # ID профиля, который отображается
        self.current_user_id = current_user_id  # ID авторизованного пользователя
        self.is_own_profile = is_own_profile
        self.setup_ui()
        self.load_user_videos()

    def setup_ui(self):
        self.setFixedSize(1002, 659)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            '''
                background: #f8e8e9;
                border: 1px solid #ccc;
                border-radius: 20px;
            '''
        )
        self.setContentsMargins(6, 15, 0, 15)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_layout.setSpacing(0)

        nickname = self.db.get_user_nickname(self.user_id)
        if nickname is None:
            nickname = 'Unknown'
        self.profile_name = nickname

        title = QLabel(f"{nickname}'s videos")
        title.setStyleSheet(''''
            font-family: 'Liberation Mono';
            font-size: 30px;
            border: none;
            background: transparent;
        ''')

        self.add_btn = QPushButton('')
        self.add_btn.setFixedSize(50, 50)
        self.add_btn.setIcon(QIcon('icons/add.svg'))
        self.add_btn.setIconSize(QSize(50, 50))
        self.add_btn.clicked.connect(self.upload_video)

        horizontal_layout.addWidget(title)
        horizontal_layout.addStretch(1)
        
        # Показываем кнопку добавления только для своего профиля
        if self.is_own_profile:
            horizontal_layout.addWidget(self.add_btn)

        top_widget = QWidget()
        top_widget = QWidget()
        top_widget.setStyleSheet(''' 
            border: none;
            margin: 0 10px;
        ''')
        top_widget.setContentsMargins(0, 0, 20, 0)
        top_widget.setLayout(horizontal_layout)

        # Вертикальный layout
        vertical_layout = QVBoxLayout(self)
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_layout.setSpacing(15)

        # Добавляем виджет с горизонтальным layout
        vertical_layout.addWidget(top_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        apply_scroll_style(self.scroll_area)

        self.container = QWidget()
        self.container.setStyleSheet('border: none')
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(12, 15, 0, 15)
        self.container_layout.setSpacing(15)

        self.scroll_area.setWidget(self.container)
        vertical_layout.addWidget(self.scroll_area)

    def load_user_videos(self):
        videos = self.db.get_videos_by_user(self.user_id)
        if not videos:
            return
        for video_id in videos:
            # Разрешаем удаление видео только для своего профиля
            video_widget = HorizontalVideoLong(self.db, video_id, can_delete=self.is_own_profile)
            self.container_layout.addWidget(video_widget)

    def refresh_videos_ui(self):
        self.clear_videos()
        self.load_user_videos()

    def upload_video(self):
        upload_dialog = UploadDialog(self.db, self.user_id, parent=self)
        upload_dialog.setModal(True)

        if hasattr(upload_dialog.upload_widget, 'upload_successful'):
            upload_dialog.upload_widget.upload_successful.connect(
                lambda video_data: self.on_video_uploaded(video_data, upload_dialog)
            )

        upload_dialog.exec()

    def on_video_uploaded(self, video_data, upload_dialog):
        try:
            upload_dialog.close()
        except Exception:
            pass

        self.refresh_videos_ui()

        self.scroll_to_top()

    def scroll_to_top(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(0)

    def clear_videos(self):
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
