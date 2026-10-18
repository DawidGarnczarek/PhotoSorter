"""App initialization."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow


def run() -> int:
    app = QApplication.instance() or QApplication([])
    win = MainWindow()
    win.show()
    return app.exec()
