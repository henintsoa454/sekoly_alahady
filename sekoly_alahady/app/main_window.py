from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from app.databases.db import SessionLocal
from app.databases.models import Eleve, Professeur, Classe

# Matplotlib pour graphique
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class GraphCanvas(FigureCanvasQTAgg):
    """Graphique embarqué dans PyQt6"""
    def __init__(self, parent=None):
        fig = Figure(figsize=(4, 3))
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # FENÊTRE PLEIN ÉCRAN
        self.setWindowTitle("Gestion École - Tableau de bord")
        self.showMaximized()

        # Layout principal
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # =============== MENU LATÉRAL =====================
        self.side_menu = QFrame()
        self.side_menu.setFixedWidth(220)
        self.side_menu.setStyleSheet("""
            background-color: #2b2d42;
            color: white;
        """)

        menu_layout = QVBoxLayout(self.side_menu)
        menu_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📚 MENU")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        menu_layout.addWidget(title)

        # Boutons du menu
        btn_dashboard = QPushButton("Tableau de bord")
        btn_eleves = QPushButton("Élèves")
        btn_professeurs = QPushButton("Professeurs")
        btn_classes = QPushButton("Classes")
        btn_examens = QPushButton("Examens")

        for btn in [btn_dashboard, btn_eleves, btn_professeurs, btn_classes, btn_examens]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3d57;
                    color: white;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #4b4f72;
                }
            """)
            menu_layout.addWidget(btn)

        menu_layout.addStretch()

        # ================== ZONE CENTRALE =======================
        self.pages = QStackedWidget()
        self.dashboard_page = self.create_dashboard_page()
        self.pages.addWidget(self.dashboard_page)

        # ==== Ajouter les écrans (tu les ajouteras plus tard) ====
        # self.pages.addWidget(ElevesScreen())
        # self.pages.addWidget(ProfesseursScreen())

        # Assignation des actions
        btn_dashboard.clicked.connect(lambda: self.pages.setCurrentWidget(self.dashboard_page))

        # Layout horizontal
        main_layout.addWidget(self.side_menu)
        main_layout.addWidget(self.pages)

        self.setCentralWidget(main_widget)

    # ================================================================
    #                   PAGE TABLEAU DE BORD
    # ================================================================
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Dashboard général")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        layout.addWidget(title)
        layout.addSpacing(20)

        # Zone statistiques
        stats_layout = QHBoxLayout()

        total_eleves = self.count_table(Eleve)
        total_profs = self.count_table(Professeur)

        lbl_eleves = self.stat_box("Nombre d'élèves", total_eleves)
        lbl_profs = self.stat_box("Nombre de professeurs", total_profs)

        stats_layout.addWidget(lbl_eleves)
        stats_layout.addWidget(lbl_profs)

        layout.addLayout(stats_layout)
        layout.addSpacing(40)

        # Graphique
        graph = self.create_class_distribution_graph()
        layout.addWidget(graph)

        return page

    # ================= UTILITAIRES =====================
    def count_table(self, model):
        session = SessionLocal()
        count = session.query(model).count()
        session.close()
        return count

    def stat_box(self, title, value):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #edf2f4;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(frame)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Arial", 14))
        lbl_value = QLabel(str(value))
        lbl_value.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        lbl_value.setStyleSheet("color: #d90429;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)

        return frame

    def create_class_distribution_graph(self):
        canvas = GraphCanvas()

        session = SessionLocal()
        classes = session.query(Classe).all()
        session.close()

        x_labels = [c.nom for c in classes]
        y_eleves = []
        y_profs = []

        for c in classes:
            s = SessionLocal()
            nb_e = s.query(Eleve).filter(Eleve.classe_id == c.id).count()
            nb_p = (
                s.query(Professeur)
                 .join(Professeur.classes)
                 .filter(Classe.id == c.id)
                 .count()
            )
            s.close()

            y_eleves.append(nb_e)
            y_profs.append(nb_p)

        ax = canvas.axes
        ax.clear()
        ax.bar(x_labels, y_eleves, label="Élèves")
        ax.bar(x_labels, y_profs, bottom=y_eleves, label="Professeurs")
        ax.set_title("Répartition élèves et professeurs par classe")
        ax.legend()

        canvas.draw()
        return canvas
