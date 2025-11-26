from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem
from app.databases.db import SessionLocal
from app.databases.models import Eleve

class StudentScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion des élèves")
        self.resize(700, 400)

        self.session = SessionLocal()

        layout = QVBoxLayout()

        form = QHBoxLayout()
        self.input_nom = QLineEdit()
        self.input_nom.setPlaceholderText("Nom")
        self.input_prenom = QLineEdit()
        self.input_prenom.setPlaceholderText("Prénom")
        self.input_classe = QLineEdit()
        self.input_classe.setPlaceholderText("Classe")
        btn_add = QPushButton("Ajouter")

        btn_add.clicked.connect(self.add_eleve)

        form.addWidget(self.input_nom)
        form.addWidget(self.input_prenom)
        form.addWidget(self.input_classe)
        form.addWidget(btn_add)

        # Tableau élèves
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Classe"])

        layout.addLayout(form)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        eleves = self.session.query(Eleve).all()

        for row_idx, e in enumerate(eleves):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(e.id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(e.nom))
            self.table.setItem(row_idx, 2, QTableWidgetItem(e.prenom))
            self.table.setItem(row_idx, 3, QTableWidgetItem(e.classe))

    def add_eleve(self):
        nom = self.input_nom.text()
        prenom = self.input_prenom.text()
        classe = self.input_classe.text()

        if nom and prenom and classe:
            eleve = Eleve(nom=nom, prenom=prenom, classe=classe)
            self.session.add(eleve)
            self.session.commit()
            self.load_data()
            self.input_nom.clear()
            self.input_prenom.clear()
            self.input_classe.clear()
