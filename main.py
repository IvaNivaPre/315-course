from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from windows.main_window import MainWindow
import sys

from db import Database
from help import get_font


def set_color_palette(app):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 231, 227))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(76, 163, 224))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)


if __name__ == "__main__":
    db = Database()
    db.init_database()
    
    # Очищаем дубликаты в истории просмотров
    deleted = db.cleanup_history_duplicates()
    if deleted > 0:
        print(f"Очищено {deleted} дубликатов из истории просмотров")

    app = QApplication(sys.argv)

    font = get_font()
    app.setFont(font)
    
    app.setStyle('Fusion')
    set_color_palette(app)
    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())