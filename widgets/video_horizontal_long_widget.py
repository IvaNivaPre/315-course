from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import Qt, QRectF, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QBitmap, QIcon

from ui.video_horizontal_long_ui import Ui_video
from widgets.confirmation_dialog import ConfirmationDialog
from db import Database


class HorizontalVideoLong(QWidget, Ui_video):
    videoClicked = pyqtSignal(int, int)

    def __init__(self, db: Database, video_id: int, watch_duration: int = None, can_delete: bool = True, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(960, 165)

        self.db = db
        self.video_id = video_id
        self.watch_duration = watch_duration if watch_duration is not None else 0
        self.can_delete = can_delete

        # Получаем информацию о видео (теперь включая длительность)
        video_info = self.db.get_video_info(self.video_id)
        if not video_info:
            return
            
        # Распаковываем данные (добавляем duration)
        username, title, _, _, views_count, upload_date, thumbnail_path, duration = video_info
        
        self.duration = duration  # Сохраняем для использования

        self.title.setText(title)
        self.nickname.setText(username)
        self.views.setText(f"{views_count} просмотров")
        self.date.setText(upload_date)

        self.remove_btn.setIcon(QIcon('icons/cross.svg'))
        self.remove_btn.setIconSize(QSize(41, 41))
        self.remove_btn.clicked.connect(self.remove_video)
        
        # Скрываем кнопку удаления, если удаление запрещено
        if not self.can_delete:
            self.remove_btn.hide()

        self.set_duration(duration)
        
        # Отображаем прогресс, если есть время просмотра
        if self.watch_duration > 0 and duration > 0:
            self.set_watch_progress(self.watch_duration, duration)

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
    
    def set_watch_progress(self, watch_duration: int, total_duration: int):
        if total_duration <= 0 or watch_duration <= 0:
            self.progress_container.setVisible(False)
            return
        
        # Откладываем отрисовку прогресса до полной инициализации виджета
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._update_progress(watch_duration, total_duration))
    
    def _update_progress(self, watch_duration: int, total_duration: int):
        """Обновляет визуальный прогресс просмотра"""
        progress_percent = min(watch_duration / total_duration, 1.0)
        
        # Используем фиксированную ширину контейнера (246 пикселей из UI)
        container_width = 246
        progress_width = int(container_width * progress_percent)
        
        self.progress_bar.setGeometry(0, 0, progress_width, 4)
        self.progress_container.setVisible(True)
        
        # Отображаем оставшееся время
        remaining = total_duration - watch_duration
        if remaining > 0:
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60
            
            if hours > 0:
                remaining_text = f"-{hours}:{minutes:02d}:{seconds:02d}"
            else:
                remaining_text = f"-{minutes}:{seconds:02d}"
            
            self.duration_label.setText(remaining_text)

    def remove_video(self):
        dialog = ConfirmationDialog(
            "Удалить видео?",
            "Вы уверены, что хотите удалить это видео?",
            self
        )

        def on_confirmed():
            self.db.delete_video(self.video_id)
            self.setParent(None)
            self.deleteLater()

            if self.parent():
                self.parent().update()

        dialog.confirmed.connect(on_confirmed)
        dialog.exec()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.remove_btn.underMouse():
                self.videoClicked.emit(self.video_id, self.watch_duration)
        super().mousePressEvent(event)