from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QBitmap

from ui.video_horizontal_ui import Ui_video


class HorizontalVideo(QWidget, Ui_video):
    def __init__(self, title: str, author: str, views: int, date: str, thumbnail_path: str, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(619, 165)

        self.title.setText(title)
        self.nickname.setText(author)
        self.views.setText(f"{views} просмотров")
        self.date.setText(date)

        pixmap = QPixmap(thumbnail_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.thumnbnail.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            mask = QBitmap(scaled.size())
            mask.fill(Qt.GlobalColor.color0)

            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, scaled.width(), scaled.height()), 20, 20)

            mask_painter = QPainter(mask)
            mask_painter.fillPath(path, Qt.GlobalColor.color1)
            mask_painter.end()

            scaled.setMask(mask)
            self.thumnbnail.setPixmap(scaled)
            self.thumnbnail.setScaledContents(True)
