from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import Qt
from datetime import datetime
from .comment_widget import CommentWidget

from help import apply_scroll_style
from db import Database


class CommentsWidget(QWidget):
    def __init__(self, db: Database = None, video_id=None, user_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.video_id = video_id
        self.user_id = user_id
        self.setFixedHeight(500)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget {
                background: #f8e8e9;
                border: none;
                border-radius: 20px;
            }
            QLabel#author {
                font-family: 'Source Sans Pro';
                font-size: 16px;
                font-weight: bold;
                color: #D45B69;
            }
            QLabel#date {
                font-family: 'Source Sans Pro';
                font-size: 16px;
                color: #888;
                margin-left: 10px;
            }
            QLabel#text {
                font-family: 'Source Sans Pro';
                font-size: 16px;
                color: #333;
                margin: 8px 0;
            }
            QScrollArea {
                border: none;
                background: #f8e8e9;
            }
        """)
        
        # Добавляем заголовок "Комментарии"
        self.comments_header = QLabel("Comments")
        self.comments_header.setStyleSheet("""
            QLabel {
                font-family: 'Liberation Mono';
                font-size: 24px;
                font-weight: bold;
                color: #D45B69;
                background: #f8e8e9;
                padding: 10px;
            }
        """)
        self.layout.addWidget(self.comments_header)
        
        # Add comment input field and send button
        self.comment_input_container = QWidget()
        self.comment_input_layout = QHBoxLayout(self.comment_input_container)
        self.comment_input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("  Write your comment here...")
        self.comment_input.setFixedHeight(80)
        self.comment_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Source Sans Pro';
                color: #000;
                font-size: 16px;
                background: white;
                border-radius: 10px;
                margin: 10px;
            }
            QTextEdit::placeholder {
                padding: 10px;
                color: #888;
                font-style: italic;
            }
        """)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(100, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                font-family: 'Source Sans Pro';
                font-size: 16px;
                font-weight: bold;
                background-color: #D45B69;
                color: white;
                border-radius: 10px;
                margin-right: 16px;
            }
            QPushButton:hover {
                background-color: #c14a58;
            }
        """)
        
        # Создаём текст для неавторизованных пользователей
        self.auth_required_label = QLabel("Авторизуйтесь для написания комментариев")
        self.auth_required_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.auth_required_label.setStyleSheet("""
            QLabel {
                font-family: 'Source Sans Pro';
                font-size: 16px;
                color: #888;
                font-style: italic;
                background: white;
                border-radius: 10px;
                margin: 10px;
                padding: 20px;
            }
        """)
        
        self.comment_input_layout.addWidget(self.comment_input)
        self.comment_input_layout.addWidget(self.send_button)
        self.comment_input_layout.addWidget(self.auth_required_label)
        self.layout.addWidget(self.comment_input_container)
        
        # Connect send button
        self.send_button.clicked.connect(self.on_send_clicked)
        
        # Устанавливаем видимость в зависимости от авторизации
        self.update_auth_ui()
        
        # Создаем ScrollArea для комментариев
        self.scroll_area = QScrollArea()
        
        self.scroll_area.setStyleSheet('''
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f9e1d4;
                width: 6px;
                margin: 0px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #d45b69;
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
        ''')
        
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # Контейнер для комментариев внутри ScrollArea
        self.comments_container = QWidget()
        self.comments_container_layout = QVBoxLayout(self.comments_container)
        self.comments_container_layout.setContentsMargins(0, 0, 0, 0)
        self.comments_container_layout.setSpacing(15)
        
        # Надпись "No comments"
        self.empty_label = QLabel("No comments")
        self.empty_label.setStyleSheet("""
            QLabel {
                font-family: 'Source Sans Pro';
                font-size: 16px;
                color: #888;
                text-align: center;
                padding: 20px;
            }
        """)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comments_container_layout.addWidget(self.empty_label)
        
        # Добавляем stretch в конец, чтобы комментарии не распределялись равномерно
        self.comments_container_layout.addStretch()
        
        self.scroll_area.setWidget(self.comments_container)
        # Scroll area занимает всё оставшееся место (stretch=1)
        self.layout.addWidget(self.scroll_area, 1)
        
        # Загружаем комментарии, если video_id установлен
        if self.video_id and self.db:
            self.load_comments()
        
    def add_comment(self, author: str, text: str, date: str, avatar_path: str = ''):
        comment = CommentWidget(author, date, text, avatar_path)
        if self.empty_label:
            self.comments_container_layout.removeWidget(self.empty_label)
            self.empty_label.deleteLater()
            self.empty_label = None
        # Добавляем комментарий перед stretch (в позицию count-1)
        insert_pos = max(0, self.comments_container_layout.count() - 1)
        self.comments_container_layout.insertWidget(insert_pos, comment)
        
    def on_send_clicked(self):
        text = self.comment_input.toPlainText().strip()
        if not text:
            return
        
        # Проверяем авторизацию
        if not self.user_id:
            print("Ошибка: пользователь не авторизован")
            return
        
        # Проверяем, что video_id установлен
        if not self.video_id:
            print("Ошибка: video_id не установлен")
            return
            
        if not self.db:
            print("Ошибка: БД не подключена")
            return
        
        try:
            # Сохраняем комментарий в БД
            self.db.add_comment(self.video_id, self.user_id, text)
            
            # Обновляем предпочтения при написании комментария
            self.db.update_preference_on_comment(self.user_id, self.video_id)
            
            # Очищаем поле ввода
            self.comment_input.clear()
            
            # Перезагружаем комментарии
            self.load_comments()
        except Exception as e:
            print(f"Ошибка при отправке комментария: {e}")
            
    def load_comments(self):
        """
        Загружает комментарии из БД
        """
        if not self.video_id or not self.db:
            return
        
        # Очищаем текущие комментарии, НО сохраняем stretch
        # Удаляем все виджеты кроме последнего элемента (stretch)
        while self.comments_container_layout.count() > 1:
            item = self.comments_container_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        
        # Сбрасываем empty_label
        self.empty_label = None
        
        # Загружаем комментарии из БД
        comments = self.db.get_video_comments(self.video_id)
        
        if not comments:
            # Показываем "No comments"
            self.empty_label = QLabel("No comments")
            self.empty_label.setStyleSheet("""
                QLabel {
                    font-family: 'Source Sans Pro';
                    font-size: 16px;
                    color: #888;
                    text-align: center;
                    padding: 20px;
                }
            """)
            self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Добавляем empty_label перед stretch
            insert_pos = max(0, self.comments_container_layout.count() - 1)
            self.comments_container_layout.insertWidget(insert_pos, self.empty_label)
        else:
            # Добавляем комментарии
            for comment in comments:
                author = comment['username']
                text = comment['text']
                # Форматируем дату
                created_at = comment['created_at']
                avatar_path = comment['pfp_path'] or ''
                
                self.add_comment(author, text, created_at, avatar_path)
    
    def set_video_id(self, video_id):
        """
        Устанавливает video_id и перезагружает комментарии
        """
        self.video_id = video_id
        if self.db:
            self.load_comments()
    
    def set_user_id(self, user_id):
        """
        Устанавливает user_id
        """
        self.user_id = user_id
        self.update_auth_ui()
    
    def update_auth_ui(self):
        """
        Обновляет UI в зависимости от статуса авторизации
        """
        if self.user_id:
            # Пользователь авторизован - показываем поле ввода и кнопку
            self.comment_input.show()
            self.send_button.show()
            self.auth_required_label.hide()
        else:
            # Пользователь не авторизован - показываем текст
            self.comment_input.hide()
            self.send_button.hide()
            self.auth_required_label.show()
    
    def clear_input(self):
        """
        Очищает поле ввода комментария
        """
        self.comment_input.clear()
    
    def refresh(self):
        """
        Обновляет комментарии
        """
        self.load_comments()