from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt

class UnauthenticatedProfileWidget(QWidget):
    loginRequested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # "No profile" label
        no_profile_label = QLabel("Нет профиля")
        no_profile_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_profile_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #666;
            margin-bottom: 20px;
        """)
        
        # Login button
        login_button = QPushButton("Авторизация/Регистрация")
        login_button.setFixedSize(238, 50)
        login_button.setStyleSheet("""
            QPushButton {
                background: #ff6d6d;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ff5252;
            }
        """)
        login_button.clicked.connect(self.loginRequested.emit)
        
        layout.addWidget(no_profile_label)
        layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)