from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

from widgets.menu_widget import MenuWidget
from widgets.topbar_widget import Topbar
from help import Page


class BasePage(QWidget):
    pageChanged = pyqtSignal(str)  # Сигнал для переключения страниц

    def __init__(self, page='main'):
        super().__init__()
        self.page = page
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Добавляем меню слева
        self.menu_widget = MenuWidget(page=self.page)
        self.menu_widget.refreshRequested.connect(self.refresh)
        main_layout.addWidget(self.menu_widget)

        self.content_widget = self.create_content_widget()
        if self.page != Page.profile:
            right_section = QWidget()
            right_section.setStyleSheet("border: none;")
            right_layout = QVBoxLayout(right_section)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(0)

            # Добавляем верхнюю панель
            self.topbar_widget = Topbar(page=self.page)
            self.topbar_widget.searchRequested.connect(self.handle_search)
            right_layout.addWidget(self.topbar_widget)

            right_layout.addWidget(self.content_widget)

            main_layout.addWidget(right_section)
        else:
            main_layout.addWidget(self.content_widget)

    def create_content_widget(self):
        return QWidget()

    def refresh(self):
        """
        Refresh the page content.
        Child classes should override this method to implement refresh logic.
        """
        pass
    
    def handle_search(self, query: str):
        """
        Handle search requests.
        Child classes should override this method to implement search logic.
        """
        pass