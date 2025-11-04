from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget

from ui.topbar_ui import Ui_topbar


class Topbar(QWidget, Ui_topbar):
    searchRequested = pyqtSignal(str)  # Сигнал поиска с текстом запроса
    
    def __init__(self, page='main', parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(1070, 92)

        self.search_btn.setIcon(QIcon('icons/search.svg'))
        self.search_btn.setIconSize(QSize(42, 42))

        if page == 'history':
            self.searchbar.setPlaceholderText('Search in history')
        
        # Подключаем сигналы поиска
        self.search_btn.clicked.connect(self.perform_search)
        self.searchbar.returnPressed.connect(self.perform_search)
    
    def perform_search(self):
        """Выполняет поиск и отправляет сигнал с текстом запроса"""
        query = self.searchbar.text().strip()
        self.searchRequested.emit(query)
