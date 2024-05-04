from typing import Tuple

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


def get_screen_size() -> Tuple[int, int]:
    # 画面のプライマリディスプレイを取得
    primary_screen = QGuiApplication.primaryScreen()
    # 画面の幅と高さを取得
    screen_size = primary_screen.size()
    width = screen_size.width()
    height = screen_size.height()
    return width, height


def float2text(x: float, _format="{:.3g}") -> str:
    return _format.format(x)


def show_warning_popup(parent: QWidget, message: str):
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(message)
    msgBox.setIcon(QMessageBox.Icon.Warning)
    msgBox.setText(message)
    msgBox.show()
