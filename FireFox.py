import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt6.QtCore import Qt, QPoint, QSize

class ModernSmallWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- 1. Основные настройки окна ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Устанавливаем размер окна 100x100
        self.setFixedSize(100, 100)

        # Переменная для перетаскивания
        self.drag_pos = QPoint()

        # --- 2. Главный контейнер (фон окна) ---
        self.main_container = QWidget()
        self.setCentralWidget(self.main_container)
        
        # Стилизация главного фона (закругление как в Win11)
        self.main_container.setStyleSheet("""
            QWidget#MainFrame {
                background-color: #1e1e1e; /* Темный фон */
                border-radius: 12px;       /* Закругление окна */
                border: 1px solid #3d3d3d;
            }
        """)
        self.main_container.setObjectName("MainFrame")
        
        # Главный лейаут (вертикальный)
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Убираем отступы
        self.main_layout.setSpacing(0)

        # --- 3. Верхняя панель (для кнопки закрытия) ---
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(20) # Очень низкая панель
        self.title_bar_layout = QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(0, 0, 2, 0) # Отступ только справа
        self.title_bar_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Кнопка-крестик
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(16, 16) # Маленькая кнопка
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.clicked.connect(self.close) # Действие при клике
        
        # Стиль кнопки закрытия
        self.close_button.setStyleSheet("""
            QPushButton {
                color: #aaaaaa;
                background-color: transparent;
                border: none;
                border-radius: 8px; /* Почти круглая */
                font-size: 14px;
                font-weight: bold;
                line-height: 16px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #e81123; /* Красный при наведении */
                color: white;
            }
        """)
        
        self.title_bar_layout.addWidget(self.close_button)
        self.main_layout.addWidget(self.title_bar)

        # --- 4. Область контента (центрирование куба) ---
        self.content_area = QWidget()
        self.main_layout.addWidget(self.content_area)
        
        # Используем Grid layout для идеального центрирования
        self.grid_layout = QGridLayout(self.content_area)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        # --- 5. Внутренний закругленный куб (50x50) ---
        self.inner_cube = QWidget()
        self.inner_cube.setFixedSize(50, 50) # Размер 50x50
        
        # Кастомизация КУБА (цвет, закругление 15px)
        self.inner_cube.setStyleSheet("""
            QWidget {
                background-color: #3a3a3a; /* Более светлый серый для контраста */
                border-radius: 15px;       /* Твое требование по закруглению */
                border: 1px solid #555555;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 7px; /* Очень маленький шрифт, чтобы влез */
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        
        # Текст внутри куба
        cube_layout = QVBoxLayout(self.inner_cube)
        cube_layout.setContentsMargins(2, 2, 2, 2)
        label = QLabel("CA")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cube_layout.addWidget(label)

        # Добавляем куб в центр grid layout
        self.grid_layout.addWidget(self.inner_cube, 0, 0, Qt.AlignmentFlag.AlignCenter)

    # --- Функции для перетаскивания окна за любую точку ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Немного увеличим шрифт интерфейса по умолчанию, чтобы крестик был виднее
    font = app.font()
    font.setPointSize(9)
    app.setFont(font)
    
    window = ModernSmallWindow()
    window.show()
    sys.exit(app.exec())