# demo_video_page.py
import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from windows.video_view_page import VideoViewPage


class DemoMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_demo_data()
        
    def setup_ui(self):
        self.setWindowTitle("Демо - Страница просмотра видео")
        self.setGeometry(100, 100, 1070, 897)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем страницу видео
        self.video_page = VideoViewPage()
        layout.addWidget(self.video_page)
        
    def load_demo_data(self):
        """Загружает демонстрационные данные"""
        # Создаем демонстрационные данные
        demo_data = {
            'title': 'Учим PyQt6: Создание современного видеоплеера',
            'author': 'Python Master',
            'views': 15427,
            'date': '15 дек. 2024 г.',
            'subscribers': 128500,
            'likes': 1247,
            'dislikes': 23,
            'pfp_path': self.get_demo_image_path('avatar.png'),
            'description': """
🎯 В этом видео мы создаем современный видеоплеер на PyQt6 с нуля!

В этом уроке вы узнаете:
• Как работать с QMediaPlayer и QVideoWidget
• Создание кастомных элементов управления
• Реализация перемотки, регулировки громкости и скорости воспроизведения
• Стилизация интерфейса с помощью CSS

📚 Полезные ссылки:
• Исходный код: github.com/pythonmaster/pyqt6-videoplayer
• Документация PyQt6: https://www.riverbankcomputing.com/static/Docs/PyQt6/
• Qt Documentation: https://doc.qt.io/

🕒 Таймкоды:
00:00 - Введение и обзор проекта
02:15 - Настройка базовой структуры плеера
08:30 - Добавление элементов управления
15:45 - Реализация функционала перемотки
22:10 - Стилизация интерфейса
28:35 - Тестирование и отладка

#pyqt6 #python #gui #videoplayer #programming
            """.strip()
        }
        
        # Устанавливаем данные на страницу
        self.video_page.set_video_data(demo_data)
        
        # Если есть демо видео, можно его загрузить
        # demo_video_path = self.get_demo_video_path()
        # if demo_video_path:
        #     self.video_page.video_player.load_video(demo_video_path)
    
    def get_demo_image_path(self, image_name):
        """Возвращает путь к демонстрационному изображению"""
        # Пытаемся найти изображение в разных местах
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'icons', image_name),
            os.path.join(os.path.dirname(__file__), 'demo_data', image_name),
            os.path.join(os.path.dirname(__file__), image_name),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Если изображение не найдено, возвращаем None
        print(f"Предупреждение: Демонстрационное изображение '{image_name}' не найдено")
        return None
    
    def get_demo_video_path(self):
        """Возвращает путь к демонстрационному видео"""
        # Пытаемся найти демо видео
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'demo_data', 'demo_video.mp4'),
            os.path.join(os.path.dirname(__file__), 'demo_video.mp4'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        print("Предупреждение: Демонстрационное видео не найдено")
        return None
    
    def closeEvent(self, event):
        """Обрабатывает закрытие приложения"""
        self.video_page.cleanup()
        super().closeEvent(event)


def main():
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль приложения
    app.setStyle('Fusion')
    
    # Создаем и показываем главное окно
    window = DemoMainWindow()
    window.show()
    
    # Запускаем главный цикл
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
