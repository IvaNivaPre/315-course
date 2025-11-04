from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from help import get_font


class ConfirmationDialog(QDialog):
    confirmed = pyqtSignal()

    def __init__(self, title, message, parent=None, dialog_type="confirmation"):
        super().__init__(parent)
        self.dialog_type = dialog_type
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)
        self.setModal(True)
        self.setup_ui(message)
        self.apply_styles()

    def setup_ui(self, message):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        if self.dialog_type == "information":
            # Информационный диалог - одна кнопка "Ok"
            self.ok_btn = QPushButton("Ok")
            self.ok_btn.setFixedSize(120, 40)
            self.ok_btn.clicked.connect(self.accept)
            
            buttons_layout.addStretch()
            buttons_layout.addWidget(self.ok_btn)
            buttons_layout.addStretch()
        else:
            # Диалог подтверждения - две кнопки "Да" и "Нет"
            self.yes_btn = QPushButton("Да")
            self.yes_btn.setFixedSize(120, 40)
            self.yes_btn.clicked.connect(self.confirm)

            self.no_btn = QPushButton("Нет")
            self.no_btn.setFixedSize(120, 40)
            self.no_btn.clicked.connect(self.reject)

            buttons_layout.addStretch()
            buttons_layout.addWidget(self.yes_btn)
            buttons_layout.addWidget(self.no_btn)
            buttons_layout.addStretch()

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #fff;
                border-radius: 15px;
                border: none;
            }
            QLabel {
                color: #000;
                font-size: 16px;
                font-weight: bold;
                padding: 30px;
                background: #f3ded4;
                border: none;
            }
            QPushButton {
                background: #ff6d6d;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
            QPushButton:pressed {
                background-color: #FF2E2E;
            }
            QPushButton:focus {
                outline: none;
            }
        """)

        font = get_font()
        font.setPointSize(12)
        font.setBold(True)
        self.message_label.setFont(font)

    def confirm(self):
        self.accept()
        self.confirmed.emit()


    @staticmethod
    def ask_confirmation(parent, title, message):
        dialog = ConfirmationDialog(title, message, parent, dialog_type="confirmation")
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted
    
    @staticmethod
    def show_information(parent, title, message):
        dialog = ConfirmationDialog(title, message, parent, dialog_type="information")
        dialog.exec()