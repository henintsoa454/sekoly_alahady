from PyQt6.QtWidgets import QApplication
from app.databases.db import init_db
from app.main_window import MainWindow

if __name__ == "__main__":
    init_db()
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
