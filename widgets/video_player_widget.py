from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QMenu,
    QToolButton, QFrame
)
from PyQt6.QtCore import QUrl, Qt, QTimer, pyqtSignal, QSize, QEvent
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QPixmap, QKeyEvent


class VideoPlayerWithControls(QWidget):
    playClicked = pyqtSignal()
    pauseClicked = pyqtSignal()

    def __init__(self, video_path: str = None, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.setup_ui()
        self.setup_media_player()
        self.setup_connections()
        self.setup_settings_menu()
        
        # Включаем фокус для обработки клавиатуры
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        if video_path:
            self.load_video(video_path)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet('''
            background: #d9d9d9;
        ''')
        self.video_widget.setFixedSize(992, 558)
        layout.addWidget(self.video_widget, stretch=1)

        self.control_panel = QFrame()
        self.control_panel.setStyleSheet(
            """
            QFrame {
                background: #f3dad4;
                padding: 4px 8px;
                border: none;
                border-bottom-left-radius: 30px;
                border-bottom-right-radius: 30px;
            }
        """
        )
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setContentsMargins(3, 0, 3, 0)
        control_layout.setSpacing(0)

        top_panel = QHBoxLayout()

        self.current_time_label = QLabel("00:00")
        self.current_time_label.setStyleSheet(
            '''
                color: black;
                font-size: 11px;
                padding-bottom: 4px;
                font-family: 'Segoe UI';
            '''
        )
        self.current_time_label.setFixedWidth(50)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #666666;
                height: 4px;
                background: #404040;
                margin: 0px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #aaaaaa;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #ff4444;
                border-radius: 2px;
            }
        """
        )

        self.remain_label = QLabel("00:00")
        self.remain_label.setStyleSheet(
            '''
                color: black;
                font-size: 11px;
                padding-bottom: 4px;
                font-family: 'Segoe UI';
            '''
        )
        self.remain_label.setFixedWidth(50)

        top_panel.addWidget(self.current_time_label)
        top_panel.addWidget(self.progress_slider, stretch=1)
        top_panel.addWidget(self.remain_label)

        bottom_panel = QHBoxLayout()
        bottom_panel.setContentsMargins(10, 0, 10, 0)
        bottom_panel.setSpacing(10)

        self.play_button = QPushButton("")
        self.play_button.setIcon(QIcon('icons/play.svg'))
        icon_size = QSize(25, 25)
        self.play_button.setIconSize(icon_size)
        self.play_button.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
            }
        """
        )
        self.play_button.setFixedSize(25, 25)

        self.rewind_button = QPushButton("")
        self.rewind_button.setIcon(QIcon('icons/5backward.svg'))
        self.rewind_button.setIconSize(QSize(30, 30))
        self.rewind_button.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
            }
        """
        )
        self.rewind_button.setFixedSize(30, 30)

        self.forward_button = QPushButton("")
        self.forward_button.setIcon(QIcon('icons/5forward.svg'))
        self.forward_button.setIconSize(QSize(30, 30))
        self.forward_button.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
            }
        """
        )
        self.forward_button.setFixedSize(30, 30)

        # Кнопка скорости воспроизведения
        self.speed_button = QToolButton()
        self.speed_button.setText("1.0x")
        self.speed_button.setStyleSheet(
            """
            QToolButton {
                background: transparent;
                color: black;
                border: none;
                padding: 4px 8px;
                font-size: 12px;
                font-family: 'Segoe UI';
            }
            QToolButton:hover {
                background: #e0c9c4;
                border-radius: 3px;
            }
        """
        )
        self.speed_button.setFixedSize(45, 25)
        self.speed_button.setToolTip("Скорость воспроизведения")
        self.speed_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 4px;
                background: #e0e0e0;
                margin: 0px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #cccccc;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #D45B69;
                border-radius: 2px;
            }
        """
        )

        self.volume_icon = QLabel()
        self.volume_icon.setFixedSize(30, 30)
        volume_pixmap = QPixmap('icons/volume.svg')
        volume_pixmap = volume_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.volume_icon.setPixmap(volume_pixmap)
        self.volume_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bottom_panel.addWidget(self.play_button)
        bottom_panel.addWidget(self.rewind_button)
        bottom_panel.addWidget(self.forward_button)
        bottom_panel.addStretch(1)
        bottom_panel.addWidget(self.volume_icon)
        bottom_panel.addWidget(self.volume_slider)
        bottom_panel.addWidget(self.speed_button)

        control_layout.addLayout(top_panel)
        control_layout.addLayout(bottom_panel)

        layout.addWidget(self.control_panel)

    def setup_media_player(self):
        """Настраивает медиаплеер"""
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        self.audio_output.setVolume(0.5)

        # Таймер для обновления UI
        self.ui_timer = QTimer()
        self.ui_timer.setInterval(100)

        # Текущие настройки
        self.playback_rate = 1.0  # Нормальная скорость

    def setup_connections(self):
        """Настраивает соединения сигналов и слотов"""
        # Кнопки управления
        self.play_button.clicked.connect(self.toggle_playback)
        self.rewind_button.clicked.connect(self.rewind_5s)
        self.forward_button.clicked.connect(self.forward_5s)
        self.volume_slider.valueChanged.connect(self.set_volume)

        # Прогресс
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        self.progress_slider.valueChanged.connect(self.slider_value_changed)

        # Медиаплеер
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.playbackStateChanged.connect(self.update_play_button)

        # Таймер UI
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start()

        # Клик по видео
        self.video_widget.mousePressEvent = self.video_clicked

    def setup_settings_menu(self):
        """Настраивает меню скорости воспроизведения"""
        self.speed_menu = QMenu(self)
        self.speed_menu.setStyleSheet(
            """
            QMenu {
                background: #f9e1d4;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 5px 15px;
                font-family: 'Segoe UI';
                color: #333;
            }
            QMenu::item:selected {
                background: #D45B69;
                color: white;
            }
        """
        )

        speed_group = QActionGroup(self)
        speed_group.setExclusive(True)

        speeds = [
            ("0.25x", 0.25),
            ("0.5x", 0.5),
            ("0.75x", 0.75),
            ("1.0x", 1.0),
            ("1.25x", 1.25),
            ("1.5x", 1.5),
            ("2.0x", 2.0)
        ]

        for name, rate in speeds:
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(rate == 1.0)
            action.triggered.connect(lambda checked, r=rate, n=name: self.set_playback_rate(r, n))
            speed_group.addAction(action)
            self.speed_menu.addAction(action)

        self.speed_button.setMenu(self.speed_menu)

    def set_playback_rate(self, rate, name):
        """Устанавливает скорость воспроизведения и обновляет текст кнопки"""
        self.playback_rate = rate
        self.media_player.setPlaybackRate(rate)
        self.speed_button.setText(name)

    def video_clicked(self, event):
        """Обрабатывает клик по видео - переключает воспроизведение/паузу"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_playback()

    def toggle_playback(self):
        """Переключает между воспроизведением и паузой"""
        if self.is_playing():
            self.pause()
            self.pauseClicked.emit()
            self.play_button.setIcon(QIcon('icons/play.svg'))
        else:
            self.play()
            self.playClicked.emit()
            self.play_button.setIcon(QIcon('icons/pause.svg'))

    def rewind_5s(self):
        """Перематывает на 5 секунд назад"""
        current_pos = self.media_player.position()
        new_pos = max(0, current_pos - 5000)  # 5000 мс = 5 секунд
        self.media_player.setPosition(new_pos)

    def forward_5s(self):
        """Перематывает на 5 секунд вперед"""
        current_pos = self.media_player.position()
        duration = self.media_player.duration()
        new_pos = min(duration, current_pos + 5000)  # 5000 мс = 5 секунд
        self.media_player.setPosition(new_pos)

    def slider_pressed(self):
        """Вызывается при нажатии на слайдер прогресса"""
        self.was_playing = self.is_playing()
        if self.was_playing:
            self.pause()
        self.ui_timer.stop()  # Останавливаем автообновление

    def slider_released(self):
        """Вызывается при отпускании слайдера прогресса - выполняем перемотку"""
        position = self.progress_slider.value()
        self.media_player.setPosition(position)
        self.ui_timer.start()  # Возобновляем автообновление

        # Возобновляем воспроизведение, если оно было активнo
        if hasattr(self, 'was_playing') and self.was_playing:
            self.play()

    def slider_value_changed(self, position):
        """Обрабатывает изменение значения слайдера без немедленной перемотки"""
        # Только обновляем время, но не перематываем
        self.current_time_label.setText(self.format_time(position))

        # Обновляем оставшееся время
        duration = self.media_player.duration()
        if duration > 0:
            remaining = duration - position
            self.remain_label.setText(f"-{self.format_time(remaining)}")

    def load_video(self, video_path: str):
        """Загружает видео из указанного пути"""
        self.video_path = video_path
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        # Автоматически запускаем воспроизведение
        QTimer.singleShot(100, self.play)

    def play(self):
        """Начинает воспроизведение видео"""
        self.media_player.play()

    def pause(self):
        """Приостанавливает воспроизведение"""
        self.media_player.pause()

    def stop(self):
        """Останавливает воспроизведение и сбрасывает позицию"""
        self.media_player.stop()

    def seek(self, position: int):
        """Перематывает видео на указанную позицию"""
        self.media_player.setPosition(position)

    def set_volume(self, value):
        """Устанавливает громкость (0-100)"""
        volume = value / 100.0  # Преобразуем в диапазон 0.0 - 1.0
        self.audio_output.setVolume(volume)

    def is_playing(self) -> bool:
        """Проверяет, воспроизводится ли видео"""
        return self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def update_position(self, position: int):
        """Обновляет позицию воспроизведения"""
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)
        self.current_time_label.setText(self.format_time(position))

        # Обновляем оставшееся время
        duration = self.media_player.duration()
        if duration > 0:
            remaining = duration - position
            self.remain_label.setText(f"-{self.format_time(remaining)}")

    def update_duration(self, duration: int):
        """Обновляет длительность видео"""
        self.progress_slider.setRange(0, duration)
        self.remain_label.setText(f"-{self.format_time(duration)}")

    def update_play_button(self, state):
        """Обновляет иконку кнопки воспроизведения"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(QIcon('pause.svg'))
        else:
            self.play_button.setIcon(QIcon('play.svg'))

    def update_ui(self):
        """Обновляет UI элементы"""
        # Обновляем прогресс, если пользователь не перемещает слайдер
        if not self.progress_slider.isSliderDown():
            position = self.media_player.position()
            self.progress_slider.setValue(position)

    def format_time(self, milliseconds: int) -> str:
        """Форматирует время в MM:SS"""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def set_video_path(self, video_path: str):
        """Устанавливает новый путь к видео"""
        self.load_video(video_path)

    def get_playback_rate(self) -> float:
        """Возвращает текущую скорость воспроизведения"""
        return self.playback_rate

    def keyPressEvent(self, event):
        """Обрабатывает нажатия клавиш"""
        if event.key() == Qt.Key.Key_Space:
            self.toggle_playback()
        elif event.key() == Qt.Key.Key_Left:
            self.rewind_5s()
        elif event.key() == Qt.Key.Key_Right:
            self.forward_5s()
        elif event.key() == Qt.Key.Key_Escape and self.video_widget.isFullScreen():
            self.video_widget.showNormal()
        else:
            super().keyPressEvent(event)

    def cleanup(self):
        """Очищает ресурсы"""
        self.stop()
        self.ui_timer.stop()
        self.media_player.setSource(QUrl())
    
    def get_position(self) -> int:
        """Получает текущую позицию воспроизведения в секундах"""
        return self.media_player.position() // 1000
    
    def set_position(self, seconds: int):
        """Устанавливает позицию воспроизведения в секундах"""
        self.media_player.setPosition(seconds * 1000)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Обработка нажатий клавиш"""
        key = event.key()
        
        # Пробел - пауза/воспроизведение
        if key == Qt.Key.Key_Space:
            self.toggle_play_pause()
            event.accept()
        
        # Левая стрелка - перемотка назад на 5 секунд
        elif key == Qt.Key.Key_Left:
            current_pos = self.media_player.position()
            new_pos = max(0, current_pos - 5000)  # -5 секунд
            self.media_player.setPosition(new_pos)
            event.accept()
        
        # Правая стрелка - перемотка вперед на 5 секунд
        elif key == Qt.Key.Key_Right:
            current_pos = self.media_player.position()
            duration = self.media_player.duration()
            new_pos = min(duration, current_pos + 5000)  # +5 секунд
            self.media_player.setPosition(new_pos)
            event.accept()
        
        # Верхняя стрелка - увеличение громкости
        elif key == Qt.Key.Key_Up:
            current_volume = self.audio_output.volume()
            new_volume = min(1.0, current_volume + 0.1)  # +10%
            self.audio_output.setVolume(new_volume)
            self.volume_slider.setValue(int(new_volume * 100))
            event.accept()
        
        # Нижняя стрелка - уменьшение громкости
        elif key == Qt.Key.Key_Down:
            current_volume = self.audio_output.volume()
            new_volume = max(0.0, current_volume - 0.1)  # -10%
            self.audio_output.setVolume(new_volume)
            self.volume_slider.setValue(int(new_volume * 100))
            event.accept()
        
        else:
            super().keyPressEvent(event)
