from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QGridLayout
from PyQt6.QtCore import Qt

from random import choice

from widgets.profile_vertical_widget import ProfileVertical
from help import apply_scroll_style


class Subscriptions(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_example_data()

    def setup_ui(self):
        self.setFixedSize(325, 659)
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

        # Заголовок
        title = QLabel("Subscriptions")
        title.setStyleSheet(
            """
            font-family: 'Liberation Mono';
            font-size: 30px;
            border: none;
            background: transparent;
            padding-left: 5px;
        """
        )
        layout.addWidget(title)

        # ScrollArea для вертикальных профилей
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        apply_scroll_style(self.scroll_area)

        # Контейнер для профилей
        self.container = QWidget()
        self.container.setStyleSheet('border: none')
        self.container_layout = QGridLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setHorizontalSpacing(15)
        self.container_layout.setVerticalSpacing(15)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)


    def load_example_data(self):
        """Загружает примеры данных"""
        subs_data = ["CodeMaster", "AI Enthusiast", "GUIGuru", "DataSciPro",
                     "WebWizard", "DesignMaster", "PythonPro", "CloudExpert",
                     "CodeMaster", "AI Enthusiast", "GUIGuru", "DataSciPro",
                     "WebWizard", "DesignMaster", "PythonPro", "CloudExpert"]

        for i, username in enumerate(subs_data):
            pfps = ['pics/rigby', 'pics/rigby_2', 'pics/rigby_3']
            profile_widget = ProfileVertical(choice(pfps))
            # Устанавливаем данные в виджет
            profile_widget.nickname.setText(username)

            # Располагаем в сетке 2 колонки
            row = i // 2
            col = i % 2
            self.container_layout.addWidget(profile_widget, row, col)

    def add_subscription(self, pfp_path, username):
        profile_widget = ProfileVertical(pfp_path)
        profile_widget.nickname.setText(username)

        count = self.container_layout.count()
        row = count // 2
        col = count % 2
        self.container_layout.addWidget(profile_widget, row, col)

    def clear_subscriptions(self):
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def refresh(self):
        self.clear_subscriptions()
        self.load_example_data()