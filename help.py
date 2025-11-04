from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtGui import QFont

import cv2


class Page:
    main = 'main'
    history = 'history'
    profile = 'profile'


def create_rounded_pixmap(pixmap, size):
    result = QPixmap(size)
    result.fill(Qt.GlobalColor.transparent)
    scaled = pixmap.scaled(
        size,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation
    )
    x = (scaled.width() - size.width()) // 2
    y = (scaled.height() - size.height()) // 2
    cropped = scaled.copy(x, y, size.width(), size.height())
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size.width(), size.height())
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, cropped)
    painter.end()
    return result


def apply_scroll_style(scroll_area):
    style = """
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
    """
    scroll_area.setStyleSheet(style)


def get_duration(file_path):
    video = cv2.VideoCapture(file_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps
    video.release()
    return int(duration)

def get_font():
    font = QFont("Segoe UI")
    font.setPointSize(10)
    return font
