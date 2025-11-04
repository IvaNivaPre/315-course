from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                            QLineEdit, QTextEdit, QComboBox, QPushButton, 
                            QFileDialog, QHBoxLayout, QCompleter, QApplication)
from PyQt6.QtCore import Qt, QRectF, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import QPixmap, QBitmap, QPainterPath, QPainter

from help import apply_scroll_style, get_duration, get_font
from db import Database


class VideoUploadWidget(QWidget):
    upload_successful = pyqtSignal(dict)

    def __init__(self, db: Database, user_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_id = user_id
        self.selected_file_path = ""
        self.selected_thumbnail_path = ""
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(650, 659)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            '''
                background: #f8e8e9;
                border: 1px solid #ccc;
                border-radius: 20px;
            '''
        )
        self.setContentsMargins(1, 15, 0, 15)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title = QLabel("Загрузить видео")
        title.setStyleSheet(
            '''
                font-size: 30px;
                border: none;
                background: transparent;
                padding-left: 5px;
            '''
        )
        layout.addWidget(title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        apply_scroll_style(self.scroll_area)

        self.container = QWidget()
        self.container.setStyleSheet('border: none; background: transparent;')
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(12, 15, 12, 15)
        self.container_layout.setSpacing(20)

        self.setup_upload_form()
        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

    def setup_upload_form(self):
        file_upload_section = self.create_upload_section()
        self.container_layout.addWidget(file_upload_section)

        thumbnail_section = self.create_thumbnail_section()
        self.container_layout.addWidget(thumbnail_section)

        # Поле для названия
        title_section = self.create_input_section("Название", QLineEdit())
        self.title_input = title_section.findChild(QLineEdit)
        self.container_layout.addWidget(title_section)

        # Поле для описания
        description_section = self.create_textarea_section("Описание", QTextEdit())
        self.description_input = description_section.findChild(QTextEdit)
        self.container_layout.addWidget(description_section)

        # Поле для категории
        self.categories = self.db.get_all_categories_names()
        category_section = self.create_combo_section("Категория", self.categories)
        self.category_combo = category_section.findChild(QComboBox)
        self.container_layout.addWidget(category_section)

        # Поле для тегов
        tags_section = self.create_input_section("Теги (через запятую)", QLineEdit())
        self.tags_input = tags_section.findChild(QLineEdit)
        tags_section.findChild(QLabel).setToolTip("Разделяйте теги запятыми, например: программирование, урок, питон")
        self.container_layout.addWidget(tags_section)

        # Label для отображения ошибок формы
        self.form_error_label = QLabel()
        self.form_error_label.setStyleSheet(
            '''
                font-size: 14px;
                color: #c62828;
                background: #ffebee;
                border: 1px solid #f44336;
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0px;
            '''
        )
        self.form_error_label.setWordWrap(True)
        self.form_error_label.setVisible(False)
        self.container_layout.addWidget(self.form_error_label)

        # Кнопка загрузки
        upload_button = QPushButton("Загрузить видео")
        upload_button.setStyleSheet(
            '''
                QPushButton {
                    background: #ff6d6d;
                    color: white;
                    border: none;
                    border-radius: 15px;
                    padding: 12px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #ff5252;
                }
                QPushButton:pressed {
                    background: #e04848;
                }
            '''
        )
        upload_button.setFixedHeight(50)
        upload_button.clicked.connect(self.upload_video)
        self.container_layout.addWidget(upload_button)

        # Добавляем растягивающийся элемент в конце
        self.container_layout.addStretch()

    def create_upload_section(self):
        section = QWidget()
        section.setStyleSheet('background: transparent; border: none;')
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label = QLabel("Видеофайл")
        label.setStyleSheet(
            '''
                font-size: 16px;
                font-weight: bold;
                color: #333;
                background: transparent;
                border: none;
            '''
        )
        layout.addWidget(label)

        # Контейнер для кнопки и информации о файле
        file_widget = QWidget()
        file_widget.setStyleSheet('background: transparent; border: none;')
        file_layout = QHBoxLayout(file_widget)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(10)

        # Кнопка выбора файла
        browse_btn = QPushButton("Обзор...")
        browse_btn.setStyleSheet(
            '''
                QPushButton {
                    background: #FF6D6D;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 8px 15px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #ff5252;
                }
            '''
        )
        browse_btn.setFixedSize(100, 35)
        browse_btn.clicked.connect(self.browse_video_file)

        # Метка для отображения выбранного файла
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setStyleSheet(
            '''
                font-size: 14px;
                color: #666;
                background: transparent;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
            '''
        )
        self.file_label.setMinimumHeight(35)
        self.file_label.setMaximumWidth(507)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        file_layout.addWidget(browse_btn)
        file_layout.addWidget(self.file_label, 1)
        layout.addWidget(file_widget)

        # Подсказка
        hint = QLabel("Поддерживаемые форматы: MP4, AVI, MOV, WMV")
        hint.setStyleSheet(
            '''
                font-size: 12px;
                color: #888;
                background: transparent;
                border: none;
            '''
        )
        layout.addWidget(hint)

        return section

    def create_thumbnail_section(self):
        section = QWidget()
        section.setStyleSheet('background: transparent; border: none;')
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label = QLabel("Превью")
        label.setStyleSheet(
            '''
                font-size: 16px;
                font-weight: bold;
                color: #333;
                background: transparent;
                border: none;
            '''
        )
        layout.addWidget(label)

        # Контейнер для кнопки и превью
        thumbnail_widget = QWidget()
        thumbnail_widget.setStyleSheet('background: transparent; border: none;')
        thumbnail_layout = QHBoxLayout(thumbnail_widget)
        thumbnail_layout.setContentsMargins(0, 0, 0, 0)
        thumbnail_layout.setSpacing(10)

        # Кнопка выбора превью
        thumbnail_btn = QPushButton("Обзор...")
        thumbnail_btn.setStyleSheet(
            '''
                QPushButton {
                    background: #FF6D6D;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 8px 15px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #ff5252;
                }
            '''
        )
        thumbnail_btn.setFixedSize(100, 35)
        thumbnail_btn.clicked.connect(self.browse_thumbnail_file)

        # Метка для отображения выбранного превью
        self.thumbnail_label = QLabel("Превью не выбрано")
        self.thumbnail_label.setStyleSheet(
            '''
                font-size: 14px;
                color: #666;
                background: transparent;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
            '''
        )
        self.thumbnail_label.setMinimumHeight(35)
        self.thumbnail_label.setMaximumWidth(507)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setMinimumWidth(200)

        # Поле для отображения превью
        self.thumbnail_preview = QLabel()
        self.thumbnail_preview.setStyleSheet(
            '''
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            '''
        )
        self.thumbnail_preview.setFixedSize(100, 68)
        self.thumbnail_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_preview.setText("Превью")
        self.thumbnail_preview.setVisible(False)

        thumbnail_layout.addWidget(thumbnail_btn)
        thumbnail_layout.addWidget(self.thumbnail_label, 1)
        thumbnail_layout.addWidget(self.thumbnail_preview)
        layout.addWidget(thumbnail_widget)

        # Подсказка
        hint = QLabel("Поддерживаемые форматы: JPG, PNG, GIF")
        hint.setStyleSheet(
            '''
                font-size: 12px;
                color: #888;
                background: transparent;
                border: none;
            '''
        )
        layout.addWidget(hint)

        return section

    def create_input_section(self, label_text, input_widget):
        section = QWidget()
        section.setStyleSheet('background: transparent; border: none;')
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label = QLabel(label_text)
        label.setStyleSheet(
            '''
                font-size: 16px;
                font-weight: bold;
                color: #333;
                background: transparent;
                border: none;
            '''
        )
        layout.addWidget(label)

        input_widget.setStyleSheet(
            '''
                QLineEdit, QTextEdit {
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 14px;
                }
                QLineEdit:focus, QTextEdit:focus {
                    border-color: #4ecdc4;
                }
            '''
        )
        input_widget.setMinimumHeight(40)
        layout.addWidget(input_widget)

        return section

    def create_textarea_section(self, label_text, text_edit):
        section = self.create_input_section(label_text, text_edit)
        text_edit.setMinimumHeight(120)
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        return section

    def create_combo_section(self, label_text, items):
        section = QWidget()
        section.setStyleSheet('background: transparent; border: none;')
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label = QLabel(label_text)
        label.setStyleSheet(
            '''
                font-size: 16px;
                font-weight: bold;
                color: #333;
                background: transparent;
                border: none;
            '''
        )
        layout.addWidget(label)

        combo = QComboBox()
        combo.addItems(items)
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # Настраиваем автодополнение
        completer = QCompleter(items, combo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        combo.setCompleter(completer)
        
        # Устанавливаем стили для редактируемого комбобокса
        combo.setStyleSheet(
            '''
                QComboBox {
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 14px;
                }
                QComboBox:focus {
                    border-color: #4ecdc4;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 30px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 5px;
                    outline: none;
                    font-size: 14px;
                }
                QComboBox QAbstractItemView::item {
                    padding: 8px;
                    border-radius: 5px;
                }
                QComboBox QAbstractItemView::item:selected {
                    background: #4ecdc4;
                    color: white;
                }
                QComboBox QAbstractItemView::item:hover {
                    background: #e0f7fa;
                }
            '''
        )
        
        combo.installEventFilter(self)
        if combo.isEditable() and combo.lineEdit():
            combo.lineEdit().installEventFilter(self)

        combo.setMinimumHeight(40)
        combo.wheelEvent = lambda event: None
        layout.addWidget(combo)

        return section
    
    


    def browse_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите видеофайл",
            "",
            "Видеофайлы (*.mp4 *.avi *.mov *.wmv *.mkv);;Все файлы (*)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            file_name = file_path.split('/')[-1]  # Берем только имя файла
            self.file_label.setText(file_name)
            self.file_label.setStyleSheet(
                '''
                    font-size: 14px;
                    color: #2e7d32;
                    background: #e8f5e9;
                    border: 1px solid #4caf50;
                    border-radius: 8px;
                    padding: 8px;
                '''
            )
            # Скрываем ошибку формы при успешном выборе файла
            self.hide_form_error()

    def browse_thumbnail_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение для превью",
            "",
            "Изображения (*.jpg *.jpeg *.png *.gif *.bmp);;Все файлы (*)"
        )
        
        if file_path:
            self.selected_thumbnail_path = file_path
            file_name = file_path.split('/')[-1]  # Берем только имя файла
            self.thumbnail_label.setText(file_name)
            self.thumbnail_label.setStyleSheet(
                '''
                    font-size: 14px;
                    color: #2e7d32;
                    background: #e8f5e9;
                    border: 1px solid #4caf50;
                    border-radius: 8px;
                    padding: 8px;
                '''
            )
            
            # Загружаем и отображаем превью
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.thumbnail_preview.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                    Qt.TransformationMode.SmoothTransformation)
                mask = QBitmap(scaled.size())
                mask.fill(Qt.GlobalColor.color0)

                path = QPainterPath()
                path.addRoundedRect(QRectF(0, 0, scaled.width(), scaled.height()), 6, 6)

                mask_painter = QPainter(mask)
                mask_painter.fillPath(path, Qt.GlobalColor.color1)
                mask_painter.end()

                scaled.setMask(mask)
                self.thumbnail_preview.setPixmap(scaled)
                self.thumbnail_preview.setScaledContents(True)
                self.thumbnail_preview.setVisible(True)

    def upload_video(self):
        # Проверяем, выбран ли файл
        if not self.selected_file_path:
            self.show_file_error("Выберите видеофайл")
            return

        # Проверяем заполнено ли название
        if not self.title_input.text().strip():
            self.show_form_error("Введите название видео")
            return
        
        category = self.category_combo.currentText()
        if category not in self.categories:
            self.show_form_error("Выберите существующую категорию")
            return

        # Собираем данные
        video_data = {
            'user_id': self.user_id,
            'file_path': self.selected_file_path,
            'thumbnail_path': self.selected_thumbnail_path,
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'category': self.category_combo.currentText(),
            'tags': [tag.strip() for tag in self.tags_input.text().split(',') if tag.strip()],
            'duration': get_duration(self.selected_file_path)
        }

        self.db.upload_video(**video_data)
        print("Загрузка видео:", video_data)
        
        # Показываем сообщение об успехе
        self.show_success("Видео успешно загружено!")
        
        # Испускаем сигнал об успешной загрузке
        self.upload_successful.emit(video_data)
        
        # Очищаем форму после успешной загрузки
        self.clear_form()

    def show_file_error(self, message):
        """Показывает ошибку связанную с файлом в file_label"""
        self.file_label.setText(message)
        self.file_label.setStyleSheet(
            '''
                font-size: 14px;
                color: #c62828;
                background: #ffebee;
                border: 1px solid #f44336;
                border-radius: 8px;
                padding: 8px;
            '''
        )

    def hide_file_error(self):
        """Сбрасывает стиль file_label к нормальному состоянию"""
        if self.selected_file_path:
            self.file_label.setStyleSheet(
                '''
                    font-size: 14px;
                    color: #2e7d32;
                    background: #e8f5e9;
                    border: 1px solid #4caf50;
                    border-radius: 8px;
                    padding: 8px;
                '''
            )
        else:
            self.file_label.setStyleSheet(
                '''
                    font-size: 14px;
                    color: #666;
                    background: transparent;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 8px;
                '''
            )

    def show_form_error(self, message):
        """Показывает ошибку формы в специальном QLabel"""
        self.form_error_label.setText(message)
        self.form_error_label.setVisible(True)
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
        self.scroll_area.verticalScrollBar().maximum()
    ))

    def hide_form_error(self):
        """Скрывает ошибку формы"""
        self.form_error_label.setVisible(False)

    def show_success(self, message):
        """Показывает сообщение об успехе"""
        self.file_label.setText(message)
        self.file_label.setStyleSheet(
            '''
                font-size: 14px;
                color: #2e7d32;
                background: #e8f5e9;
                border: 1px solid #4caf50;
                border-radius: 8px;
                padding: 8px;
            '''
        )
        # Скрываем ошибку формы при успехе
        self.hide_form_error()

    def clear_form(self):
        self.selected_file_path = ""
        self.selected_thumbnail_path = ""
        self.file_label.setText("Файл не выбран")
        self.file_label.setStyleSheet(
            '''
                font-size: 14px;
                color: #666;
                background: transparent;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
            '''
        )
        self.thumbnail_label.setText("Превью не выбрано")
        self.thumbnail_label.setStyleSheet(
            '''
                font-size: 14px;
                color: #666;
                background: transparent;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
            '''
        )
        self.thumbnail_preview.setVisible(False)
        self.thumbnail_preview.clear()
        self.title_input.clear()
        self.description_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.tags_input.clear()
        self.hide_form_error()