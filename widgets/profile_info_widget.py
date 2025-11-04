from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QIcon

from ui.profile_info_ui import Ui_profileInfo
from help import create_rounded_pixmap
from db import Database
from widgets.confirmation_dialog import ConfirmationDialog


class ProfileInfo(QWidget, Ui_profileInfo):
    logoutRequested = pyqtSignal()
    
    def __init__(self, db: Database, user_id, current_user_id=None, is_own_profile=True, page='main', parent=None):
        super().__init__(parent)
        self.db = db
        self.user_id = user_id  # ID профиля, который отображается
        self.current_user_id = current_user_id  # ID авторизованного пользователя
        self.is_own_profile = is_own_profile
        self.is_subscribed = False
        self.setupUi(self)
        self.setFixedSize(1000, 176)

        user_info = db.get_user_info(user_id)
        if user_info:
            nickname, pfp_path, subscribers = user_info
        else:
            nickname = 'Unknown'
            pfp_path = 'pics/car.jpg'
            subscribers = 0

        self.nickname.setText(nickname)
        self.subscribers.setText(f"{subscribers} подписчиков")

        # Настраиваем кнопки в зависимости от того, свой это профиль или чужой
        # Кнопка выхода
        self.logout_btn.setIcon(QIcon('icons/logout.svg'))
        self.logout_btn.setIconSize(QSize(41, 41))
        self.logout_btn.clicked.connect(self.confirm_logout)
        
        if self.is_own_profile:
            # Свой профиль - показываем кнопку выхода, скрываем подписку
            self.logout_btn.show()
            self.subscribe_btn.hide()
        else:
            # Чужой профиль - скрываем выход, показываем подписку
            self.logout_btn.hide()
            self.subscribe_btn.show()
            self.subscribe_btn.clicked.connect(self.on_subscribe_clicked)
            
            # Проверяем, подписаны ли мы уже
            if self.current_user_id:
                self.is_subscribed = self.db.is_subscribed(self.current_user_id, self.user_id)
                self.update_subscribe_button()

        pixmap = QPixmap(pfp_path)
        if pixmap.isNull():
            placeholder = QPixmap(self.pfp.width(), self.pfp.height())
            placeholder.fill(QColor("#ccc"))
            rounded_pixmap = create_rounded_pixmap(placeholder, self.pfp.size())
            self.pfp.setPixmap(rounded_pixmap)
        else:
            rounded_pixmap = create_rounded_pixmap(pixmap, self.pfp.size())

        self.pfp.setPixmap(rounded_pixmap)
        self.pfp.setScaledContents(True)

        self.pfp.setStyleSheet('''
            QLabel {
                border-radius: 40px;
                border: none;
            }
            QLabel:hover {
                background-color: #ccc;
            }
        ''')
    
    def mousePressEvent(self, event):
        """Handle mouse click event"""
        # Смена фото только для своего профиля
        if self.is_own_profile and self.pfp.underMouse() and event.button() == Qt.MouseButton.LeftButton:
            self.change_profile_picture()
        else:
            super().mousePressEvent(event)
            
    def change_profile_picture(self):
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите новое фото", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            new_pixmap = QPixmap(file_path)
            if not new_pixmap.isNull():
                label_size = self.pfp.size()
                rounded_pixmap = create_rounded_pixmap(new_pixmap, label_size)
                self.pfp.setPixmap(rounded_pixmap)

    def confirm_logout(self):
        dialog = ConfirmationDialog(
            "Подтверждение выхода",
            "Вы уверены, что хотите выйти?",
            self
        )

        def on_confirmed():
            self.logoutRequested.emit()

        dialog.confirmed.connect(on_confirmed)
        dialog.exec()

    def on_subscribe_clicked(self):
        """Обработка нажатия на кнопку подписки"""
        if not self.current_user_id:
            ConfirmationDialog.show_information(self, "Авторизация", "Авторизуйтесь, чтобы подписаться на канал")
            return
        
        if self.is_subscribed:
            self.db.unsubscribe(self.current_user_id, self.user_id)
            self.is_subscribed = False
        else:
            self.db.subscribe(self.current_user_id, self.user_id)
            self.is_subscribed = True
        
        self.update_subscribe_button()
        self.refresh()
    
    def update_subscribe_button(self):
        """Обновляет внешний вид кнопки подписки"""
        if self.is_subscribed:
            self.subscribe_btn.setText("Отписаться")
            self.subscribe_btn.setStyleSheet("""
                QPushButton {
                    background: #E0E0E0;
                    border: 1px solid #ccc;
                    border-radius: 15px;
                    color: #606060;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
        else:
            self.subscribe_btn.setText("Subscribe")
            self.subscribe_btn.setStyleSheet("""
                QPushButton {
                    background: #FF6D6D;
                    border: 1px solid #ccc;
                    border-radius: 15px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
            """)
    
    def refresh(self):
        subscribers_count = self.db.get_user_subscribers_count(self.user_id)
        self.subscribers.setText(f"{subscribers_count} подписчиков")