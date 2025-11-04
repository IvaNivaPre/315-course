from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QColor

from help import create_rounded_pixmap

class CommentWidget(QWidget):
    def __init__(self, author: str, date: str, text: str, avatar_path: str = "", parent=None):
        super().__init__(parent)
        self.avatar_path = avatar_path
        self.setup_ui(author, date, text)
        
    def setup_ui(self, author: str, date: str, text: str):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("comment_widget")
        self.setStyleSheet("""
            background: #f3ded4;
            border-radius: 20px;
            margin: 10px;
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        top_row = QWidget()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(10, 0, 0, 0)
        top_row_layout.setSpacing(8)  # небольшое расстояние между элементами
        top_row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        # Avatar
        avatar_label = QLabel()
        avatar_label.setObjectName("avatar")
        avatar_label.setFixedSize(30, 30)

        avatar_label.setStyleSheet("""
            QLabel#avatar {
                padding: 0;
                margin: 0;
                background: transparent;
            }
        """)

        pixmap = QPixmap(self.avatar_path)
        avatar_size = QSize(30, 30)

        if not pixmap.isNull():
            rounded = create_rounded_pixmap(pixmap, avatar_size)
            avatar_label.setPixmap(rounded)
        else:
            # создаём серую заглушку как pixmap и тоже обрезаем кругом
            placeholder = QPixmap(avatar_size.width(), avatar_size.height())
            placeholder.fill(QColor("#ccc"))
            rounded_placeholder = create_rounded_pixmap(placeholder, avatar_size)
            avatar_label.setPixmap(rounded_placeholder)

        author_label = QLabel(author)
        author_label.setObjectName("author")
        author_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        date_label = QLabel(date)
        date_label.setObjectName("date")
        date_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        top_row_layout.addWidget(avatar_label)
        top_row_layout.addWidget(author_label)
        top_row_layout.addStretch()   # толкает дату вправо, а автор остаётся рядом с аватаром
        top_row_layout.addWidget(date_label)
        
        text_label = QLabel(text)
        text_label.setObjectName("text")
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            QLabel {
                font-family: 'Source Sans Pro';
                font-size: 14px;
                color: #333;
                background: transparent;
                border: none;
                border-radius: 20px;
            }
        """)
        
        layout.addWidget(top_row)
        layout.addWidget(text_label)
