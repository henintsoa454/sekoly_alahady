from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem
from app.databases.db import SessionLocal
from app.databases.models import Professeur

class TeacherScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion des professeurs")
        self.resize(700, 400)

        self.session = SessionLocal()

        layout = QVBoxLayout()

        form = QHBoxLayout()
        self.input_nom = QLineEdit()
        self.input_nom.setPlaceholderText("Nom")
        self.input_specialite = QLineEdit()
        self.input_specialite.setPlaceholderText("Spécialité")
        btn_add = QPushButton("Ajouter")

        btn_add.clicked.connect(self.add_prof)

        form.addWidget(self.input_nom)
        form.addWidget(self.input_specialite)
        form.addWidget(btn_add)

        # Tableau professeurs
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Spécialité"])

        layout.addLayout(form)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        profs = self.session.query(Professeur).all()

        for row_idx, p in enumerate(profs):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(p.nom))
            self.table.setItem(row_idx, 2, QTableWidgetItem(p.specialite))

    def add_prof(self):
        nom = self.input_nom.text()
        specialite = self.input_specialite.text()

        if nom and specialite:
            prof = Professeur(nom=nom, specialite=specialite)
            self.session.add(prof)
            self.session.commit()
            self.load_data()
            self.input_nom.clear()
            self.input_specialite.clear()
