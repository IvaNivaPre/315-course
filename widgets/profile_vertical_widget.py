from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QBitmap
from PyQt6.QtCore import Qt, QRectF, QSize

from ui.profile_vertical_ui import Ui_Form
from help import create_rounded_pixmap


class ProfileVertical(QWidget, Ui_Form):
    def __init__(self, pfp_path, page='main', parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(100, 124)

        pixmap = QPixmap(pfp_path)
        if pixmap.isNull():
            raise ValueError(f"Failed to load image: {pfp_path}")

        label_size = self.pfp.size()
        rounded_pixmap = create_rounded_pixmap(pixmap, label_size)

        self.pfp.setPixmap(rounded_pixmap)
        self.pfp.setScaledContents(True)
