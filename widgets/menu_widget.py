from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QPushButton

from ui.menu_ui import Ui_Menu


class MenuWidget(QWidget, Ui_Menu):
    pageChanged = pyqtSignal(str)
    refreshRequested = pyqtSignal()  # New signal for refresh

    def __init__(self, page='main', parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(131, 897)

        self.home_btn.setIcon(QIcon('icons/home.svg'))
        self.history_btn.setIcon(QIcon('icons/history.svg'))
        self.profile_btn.setIcon(QIcon('icons/profile.svg'))

        icon_size = QSize(86, 86)
        self.home_btn.setIconSize(icon_size)
        self.history_btn.setIconSize(icon_size)
        self.profile_btn.setIconSize(icon_size)

        self.home_btn.clicked.connect(lambda: self.pageChanged.emit('main'))
        self.history_btn.clicked.connect(lambda: self.pageChanged.emit('history'))
        self.profile_btn.clicked.connect(lambda: self.pageChanged.emit('profile'))

        match page:
            case 'main':
                self.home_btn.setIcon(QIcon('icons/home_selected.svg'))
            case 'history':
                self.history_btn.setIcon(QIcon('icons/history_selected.svg'))
            case 'profile':
                self.profile_btn.setIcon(QIcon('icons/profile_selected.svg'))
        
        # Add refresh button at the bottom
        
        self.refresh_btn.setIcon(QIcon('icons/refresh.svg'))
        self.refresh_btn.setIconSize(QSize(50, 50))
        self.refresh_btn.clicked.connect(self.refreshRequested.emit)
