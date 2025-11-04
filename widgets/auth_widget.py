from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QFormLayout, 
                            QLineEdit, QPushButton, QLabel, QMessageBox, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
from validate import validate_email, validate_password, validate_nickname


class AuthWidget(QWidget):
    loggedIn = pyqtSignal(int)  # Signal emitted with user_id when authenticated
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setFixedSize(500, 620)
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
        layout.setSpacing(0)  # Уменьшил spacing для поднятия QTabWidget выше

        title = QLabel("Login or Register")
        title.setStyleSheet(
            '''
                font-size: 30px;
                border: none;
                background: transparent;
                padding-left: 5px;
            '''
        )
        layout.addWidget(title)

        self.container = QWidget()
        self.container.setStyleSheet('border: none; background: transparent;')
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(12, 5, 12, 15)  # Уменьшил верхний отступ
        self.container_layout.setSpacing(10)

        # Tab widget for Login/Register
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            '''
                QTabWidget::pane {
                    border: none;
                    border-radius: 22px;
                    background: white;
                }
                QTabWidget::tab-bar {
                    alignment: center;
                }
                QTabBar::tab {
                    background: #e6e6e6;
                    border: none;
                    border-bottom: none;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    padding: 12px 25px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #666;
                }
                QTabBar::tab:first {
                    margin-left: 250px;
                }
                QTabBar::tab:selected {
                    background: #ff6d6d;
                    color: white;
                }
                QTabBar::tab:hover:!selected {
                    background: #d2d2d2;
                }
            '''
        )
        self.tabs.setFixedHeight(530)
        
        # Connect tab change signal to hide errors
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Login tab
        login_tab = QWidget()
        login_tab.setStyleSheet('background: transparent; border: none;')
        login_layout = QVBoxLayout(login_tab)
        login_layout.setContentsMargins(20, 20, 20, 20)
        login_layout.setSpacing(15)
        
        self.login_email = self.create_styled_input("Email:")
        self.login_password = self.create_styled_input("Password:", is_password=True)
        
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet(
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
        login_btn.setFixedHeight(50)
        login_btn.clicked.connect(self.handle_login)
        
        # Error label for login
        self.login_error_label = QLabel()
        self.login_error_label.setStyleSheet(
            '''
                font-size: 14px;
                color: #c62828;
                background: #ffebee;
                border: 1px solid #f44336;
                border-radius: 8px;
                padding: 8px;
                margin: 0px;
            '''
        )
        self.login_error_label.setWordWrap(True)
        self.login_error_label.setVisible(False)
        self.login_error_label.setFixedHeight(0)  # Start with zero height
        
        login_layout.addWidget(self.login_email)
        login_layout.addWidget(self.login_password)
        login_layout.addWidget(login_btn)
        login_layout.addWidget(self.login_error_label)
        login_layout.addStretch()
        
        # Register tab
        register_tab = QWidget()
        register_tab.setStyleSheet('background: transparent; border: none;')
        register_layout = QVBoxLayout(register_tab)
        register_layout.setContentsMargins(20, 20, 20, 20)
        register_layout.setSpacing(15)
        
        self.register_nickname = self.create_styled_input("Nickname:")
        self.register_email = self.create_styled_input("Email:")
        self.register_password = self.create_styled_input("Password:", is_password=True)
        self.register_confirm_password = self.create_styled_input("Confirm Password:", is_password=True)
        
        register_btn = QPushButton("Register")
        register_btn.setStyleSheet(
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
        register_btn.setFixedHeight(50)
        register_btn.clicked.connect(self.handle_register)
        
        # Error label for register
        self.register_error_label = QLabel()
        self.register_error_label.setStyleSheet(
            '''
                font-size: 14px;
                color: #c62828;
                background: #ffebee;
                border: 1px solid #f44336;
                border-radius: 8px;
                padding: 8px;
                margin: 0px;
            '''
        )
        self.register_error_label.setWordWrap(True)
        self.register_error_label.setVisible(False)
        self.register_error_label.setFixedHeight(0)  # Start with zero height
        
        register_layout.addWidget(self.register_nickname)
        register_layout.addWidget(self.register_email)
        register_layout.addWidget(self.register_password)
        register_layout.addWidget(self.register_confirm_password)
        register_layout.addWidget(register_btn)
        register_layout.addWidget(self.register_error_label)
        register_layout.addStretch()
        
        self.tabs.addTab(login_tab, "Login")
        self.tabs.addTab(register_tab, "Register")
        
        self.container_layout.addWidget(self.tabs)
        layout.addWidget(self.container)

        layout.addStretch()

    def create_styled_input(self, label_text, is_password=False):
        container = QWidget()
        container.setStyleSheet('background: transparent; border: none;')
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
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
        
        input_field = QLineEdit()
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        
        input_field.setStyleSheet(
            '''
                QLineEdit {
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #4ecdc4;
                }
            '''
        )
        input_field.setMinimumHeight(40)
        layout.addWidget(input_field)
        
        return container
    
    def on_tab_changed(self, index):
        """Hide error messages when tab changes"""
        self.hide_error(is_login=True)   # Hide login error
        self.hide_error(is_login=False)  # Hide register error
    
    def show_error(self, message, is_login=True):
        """Show error message under the appropriate button"""
        if is_login:
            self.login_error_label.setText(message)
            self.login_error_label.setVisible(True)
            # Calculate needed height for the error message
            self.login_error_label.setFixedHeight(self.login_error_label.sizeHint().height())
        else:
            self.register_error_label.setText(message)
            self.register_error_label.setVisible(True)
            # Calculate needed height for the error message
            self.register_error_label.setFixedHeight(self.register_error_label.sizeHint().height())
    
    def hide_error(self, is_login=True):
        """Hide error message"""
        if is_login:
            self.login_error_label.setVisible(False)
            self.login_error_label.setFixedHeight(0)
        else:
            self.register_error_label.setVisible(False)
            self.register_error_label.setFixedHeight(0)
    
    def show_success(self, message):
        """Show success message"""
        QMessageBox.information(self, "Success", message)
    
    def handle_login(self):
        email = self.login_email.findChild(QLineEdit).text().strip().lower()
        password = self.login_password.findChild(QLineEdit).text()
        
        if not email or not password:
            self.show_error("Please fill in all fields", is_login=True)
            return
        
        # Validate email format
        if not validate_email(email):
            self.show_error("Please enter a valid email address", is_login=True)
            return
        
        # Hide error if fields are filled
        self.hide_error(is_login=True)
        
        # Validate credentials against database
        user = self.db.get_user_by_email(email)
        if user and user['password'] == password:  # In real app, use hashed passwords
            self.loggedIn.emit(user['id'])
            self.show_success("Login successful!")
        else:
            self.show_error("Invalid email or password", is_login=True)
    
    def handle_register(self):
        nickname = self.register_nickname.findChild(QLineEdit).text().strip()
        email = self.register_email.findChild(QLineEdit).text().strip().lower()
        password = self.register_password.findChild(QLineEdit).text()
        confirm_password = self.register_confirm_password.findChild(QLineEdit).text()
        
        # Basic validation
        if not nickname or not email or not password or not confirm_password:
            self.show_error("Please fill in all fields", is_login=False)
            return
        
        # Validate nickname
        nickname_result = validate_nickname(nickname)
        if not nickname_result["is_valid"]:
            self.show_error(nickname_result["message"], is_login=False)
            return
        
        # Validate email
        email_result = validate_email(email)
        if not email_result["is_valid"]:
            self.show_error(email_result["message"], is_login=False)
            return
        
        # Validate password
        password_result = validate_password(password, confirm_password)
        if not password_result["is_valid"]:
            self.show_error(password_result["message"], is_login=False)
            return
        
        # Hide error if all validations pass
        self.hide_error(is_login=False)
        
        # Check if email already exists
        if self.db.get_user_by_email(email):
            self.show_error("Email already exists. Please use a different email.", is_login=False)
            return
        
        # Create new user in database
        user_id = self.db.create_user(nickname, email, password)
        if user_id:
            self.show_success("Registration successful! You can now login.")
            self.loggedIn.emit(user_id)
        else:
            self.show_error("Registration failed. Please try again.", is_login=False)