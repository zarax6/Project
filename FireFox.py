import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from PyQt6.QtCore import QFileInfo, QPoint, QTimer, Qt, QSize
    from PyQt6.QtGui import QAction, QCursor
    from PyQt6.QtWidgets import (
        QApplication,
        QFileDialog,
        QFileIconProvider,
        QGridLayout,
        QHBoxLayout,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QStyle,
        QToolButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PySide6.QtCore import QFileInfo, QPoint, QTimer, Qt, QSize
    from PySide6.QtGui import QAction, QCursor
    from PySide6.QtWidgets import (
        QApplication,
        QFileDialog,
        QFileIconProvider,
        QGridLayout,
        QHBoxLayout,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QStyle,
        QToolButton,
        QVBoxLayout,
        QWidget,
    )

from desktop_winapi import apply_desktop_window_mode


CONFIG_PATH = Path(__file__).with_name("widget_config.json")


class AppLaunchButton(QToolButton):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.setFixedSize(50, 50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setIconSize(QSize(28, 28))
        self.setAutoRaise(False)
        self.setStyleSheet(
            """
            QToolButton {
                background-color: #3a3a3a;
                border-radius: 15px;
                border: 1px solid #555555;
                padding: 0px;
            }
            QToolButton:hover {
                background-color: #4a4a4a;
            }
            QToolButton:pressed {
                background-color: #2d2d2d;
            }
            """
        )
        self.update_icon(None)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_window.launch_selected_app()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.parent_window.selected_app_path:
            self.parent_window.choose_application()
            event.accept()
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.parent_window.show_cube_menu(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def update_icon(self, app_path):
        if app_path and Path(app_path).exists():
            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(app_path))
            if not icon.isNull():
                self.setIcon(icon)
                self.setText("")
                self.setToolTip(
                    "Двойной клик запускает приложение.\n"
                    "Правый клик позволяет сменить или очистить путь."
                )
                return

        fallback_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.setIcon(fallback_icon)
        self.setText("")
        self.setToolTip(
            "Приложение не выбрано.\n"
            "Правый клик, чтобы указать .exe."
        )


class Widget_1(QMainWindow):
    def __init__(self):
        super().__init__()

        self.desktop_mode_applied = False
        self.drag_pos = QPoint()
        self.selected_app_path = ""

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnBottomHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(100, 100)

        self.main_container = QWidget()
        self.setCentralWidget(self.main_container)
        self.main_container.setObjectName("MainFrame")
        self.main_container.setStyleSheet(
            """
            QWidget#MainFrame {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #3d3d3d;
            }
            """
        )

        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(20)
        self.title_bar_layout = QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(0, 0, 2, 0)
        self.title_bar_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.close_button = QPushButton("x")
        self.close_button.setFixedSize(16, 16)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                color: #aaaaaa;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                line-height: 16px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
            """
        )

        self.title_bar_layout.addWidget(self.close_button)
        self.main_layout.addWidget(self.title_bar)

        self.content_area = QWidget()
        self.main_layout.addWidget(self.content_area)

        self.grid_layout = QGridLayout(self.content_area)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.app_button = AppLaunchButton(self)
        self.grid_layout.addWidget(self.app_button, 0, 0, Qt.AlignmentFlag.AlignCenter)

        self.load_config()
        self.refresh_button_icon()

    def showEvent(self, event):
        super().showEvent(event)
        if not self.desktop_mode_applied:
            self.desktop_mode_applied = True
            QTimer.singleShot(0, self.apply_desktop_mode)

    def apply_desktop_mode(self):
        if sys.platform != "win32":
            return
        apply_desktop_window_mode(int(self.winId()))

    def show_cube_menu(self, global_pos):
        menu = QMenu(self)
        choose_action = QAction("Выбрать приложение", self)
        choose_action.triggered.connect(self.choose_application)
        menu.addAction(choose_action)

        clear_action = QAction("Очистить приложение", self)
        clear_action.triggered.connect(self.clear_application)
        clear_action.setEnabled(bool(self.selected_app_path))
        menu.addAction(clear_action)

        menu.exec(global_pos if isinstance(global_pos, QPoint) else QCursor.pos())

    def choose_application(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите приложение",
            self.selected_app_path or str(Path.home()),
            "Приложения (*.exe);;Все файлы (*.*)",
        )
        if not file_path:
            return

        self.selected_app_path = file_path
        self.save_config()
        self.refresh_button_icon()

    def clear_application(self):
        self.selected_app_path = ""
        self.save_config()
        self.refresh_button_icon()

    def launch_selected_app(self):
        if not self.selected_app_path or not Path(self.selected_app_path).exists():
            self.choose_application()
            return

        try:
            subprocess.Popen([self.selected_app_path], shell=False)
        except OSError as error:
            QMessageBox.critical(
                self,
                "Ошибка запуска",
                f"Не удалось открыть приложение:\n{self.selected_app_path}\n\n{error}",
            )

    def refresh_button_icon(self):
        self.app_button.update_icon(self.selected_app_path)

    def load_config(self):
        if not CONFIG_PATH.exists():
            return

        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self.selected_app_path = data.get("app_path", "")

    def save_config(self):
        data = {"app_path": self.selected_app_path}
        CONFIG_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("DesktopWidget")

    font = app.font()
    font.setPointSize(9)
    app.setFont(font)

    window = Widget_1()
    window.show()
    sys.exit(app.exec())
