# video_tile_widget.py
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPixmap, QBitmap, QPainterPath, QPainter
from PyQt6.QtWidgets import QWidget

from ui.video_ui import Ui_video
from db import Database

class VideoTileWidget(QWidget, Ui_video):
    videoClicked = pyqtSignal(int)  # Сигнал при клике на видео
    
    def __init__(self, db: Database, video_id: int, parent=None):
        super().__init__(parent)
        self.db = db
        self.video_id = video_id
        self.setupUi(self)
        self.setFixedSize(330, 226)

        video_info = self.db.get_video_info(video_id)
        if not video_info:
            return

        username, title, _, _, views_count, upload_date, thumbnail, duration = video_info
            
        self.title.setText(title)
        self.nickname.setText(username)
        self.views.setText(f"{views_count} просмотров")
        self.date.setText(upload_date)

        self.set_duration(duration)

        pixmap = QPixmap(thumbnail)
        if not pixmap.isNull():
            scaled = pixmap.scaled(self.thumnbnail.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                   Qt.TransformationMode.SmoothTransformation)
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

    def set_duration(self, duration_seconds: int):
        if duration_seconds <= 0:
            self.duration_label.setText("0:00")
            return
            
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        
        if hours > 0:
            duration_text = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            duration_text = f"{minutes}:{seconds:02d}"
            
        self.duration_label.setText(duration_text)
    
    def mousePressEvent(self, event):
        self.videoClicked.emit(self.video_id)
        super().mousePressEvent(event)