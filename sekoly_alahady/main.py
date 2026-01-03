from PyQt6.QtWidgets import QApplication
from app.databases.db import init_db
from app.main_window import MainWindow
from app.databases.initialize_data import DatabaseManager

if __name__ == "__main__":
    init_db()
    DatabaseManager.initialize_default_data()
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
