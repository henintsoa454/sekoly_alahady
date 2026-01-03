from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QSizePolicy,
    QGridLayout, QMessageBox
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from app.databases.db import SessionLocal
from app.databases.models import Eleve, Professeur, Classe, professeur_classes
from app.screens.student_screen import StudentScreen  
from app.screens.teacher_screen import TeacherScreen
from app.screens.note_saisie_screen import NoteSaisieScreen  # Nouvelle page
from app.screens.settings_screen import SettingsScreen  # Page paramètres

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class GraphCanvas(FigureCanvasQTAgg):
    """Graphique embarqué avec style moderne"""
    def __init__(self, parent=None):
        fig = Figure(figsize=(6, 4), facecolor='#f5f6fa') 
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('#ffffff')
        super().__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.setWindowTitle("Gestion École - Tableau de bord")
        self.setMinimumSize(1400, 800)
        
        # Widget central
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =============== MENU LATÉRAL AMÉLIORÉ =====================
        self.side_menu = QFrame()
        self.side_menu.setFixedWidth(280)
        self.side_menu.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e1f29, stop:1 #2b2d3c);
                color: white;
                border: none;
            }
            QLabel {
                color: white;
            }
        """)

        menu_layout = QVBoxLayout(self.side_menu)
        menu_layout.setContentsMargins(20, 30, 20, 30)
        menu_layout.setSpacing(15)

        # En-tête du menu
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 20)
        
        title = QLabel("SSA Ambohinambo")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #4070f4; padding: 10px 0px;")
        header_layout.addWidget(title)
        
        self.menu_subtitle = QLabel("")
        self.menu_subtitle.setFont(QFont("Segoe UI", 12))
        self.menu_subtitle.setStyleSheet("color: #a0a0a0;")
        header_layout.addWidget(self.menu_subtitle)
        
        menu_layout.addWidget(header_widget)

        # Boutons du menu
        menu_buttons = [
            ("Tableau de bord", "tableau"),
            ("Gestion Élèves", "eleves"), 
            ("Gestion Professeurs", "professeurs"),
            ("Saisie Notes", "notes"),
            ("Paramètres", "settings")
        ]

        self.menu_btn_group = []
        for text, tag in menu_buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.setProperty("menu_tag", tag)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2b2d3c;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 15px;
                    padding: 12px;
                    text-align: left;
                    font-weight: normal;
                }
                QPushButton:hover {
                    background-color: #4070f4;
                    font-weight: bold;
                }
                QPushButton:pressed {
                    background-color: #3050c0;
                }
            """)
            menu_layout.addWidget(btn)
            self.menu_btn_group.append(btn)

        menu_layout.addStretch()

        # Footer du menu
        footer_label = QLabel("© 2024 Gestion École")
        footer_label.setStyleSheet("color: #666; font-size: 12px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(footer_label)

        # ================== ZONE CENTRALE =======================
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("""
            QStackedWidget {
                background-color: #f5f6fa;
                border: none;
            }
        """)
        
        # Création des pages
        self.dashboard_page = self.create_dashboard_page()
        self.eleve_page = StudentScreen()
        self.professor_page = TeacherScreen()
        self.note_saisie_page = NoteSaisieScreen()  # Nouvelle page de saisie de notes
        self.settings_page = SettingsScreen()  # Page paramètres
        
        # Ajout des pages au QStackedWidget
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.eleve_page)
        self.pages.addWidget(self.professor_page)
        self.pages.addWidget(self.note_saisie_page)
        self.pages.addWidget(self.settings_page)
        
        # Configuration des boutons du menu
        self.setup_menu_connections()

        # Assemblage du layout principal
        main_layout.addWidget(self.side_menu)
        main_layout.addWidget(self.pages, 1)

        # Afficher la fenêtre après initialisation complète
        QTimer.singleShot(100, self.showMaximized)

    def setup_menu_connections(self):
        """Configure les connexions des boutons du menu"""
        # Tableau de bord
        self.menu_btn_group[0].clicked.connect(lambda: self.switch_page(0, "Tableau de bord"))
        
        # Gestion des élèves
        self.menu_btn_group[1].clicked.connect(lambda: self.switch_page(1, "Gestion des Élèves"))
        
        # Gestion des professeurs
        self.menu_btn_group[2].clicked.connect(lambda: self.switch_page(2, "Gestion des Professeurs"))
        
        # Saisie de notes
        self.menu_btn_group[3].clicked.connect(lambda: self.switch_page(3, "Saisie de Notes"))
        
        # Paramètres
        self.menu_btn_group[4].clicked.connect(lambda: self.switch_page(4, "Paramètres"))

    def switch_page(self, page_index, page_title):
        """Change de page et met à jour le sous-titre"""
        self.pages.setCurrentIndex(page_index)
        self.menu_subtitle.setText(page_title)
        
        # Mettre à jour le style des boutons
        for i, btn in enumerate(self.menu_btn_group):
            if i == page_index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4070f4;
                        color: white;
                        border: none;
                        border-radius: 12px;
                        font-size: 15px;
                        padding: 12px;
                        text-align: left;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2b2d3c;
                        color: white;
                        border: none;
                        border-radius: 12px;
                        font-size: 15px;
                        padding: 12px;
                        text-align: left;
                        font-weight: normal;
                    }
                    QPushButton:hover {
                        background-color: #4070f4;
                        font-weight: bold;
                    }
                    QPushButton:pressed {
                        background-color: #3050c0;
                    }
                """)

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # En-tête de page
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Tableau de bord général")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e1f29; margin-bottom: 5px;")
        
        subtitle = QLabel("Vue d'ensemble de votre établissement")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #7f8c8d;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header_widget)

        # Section statistiques avec grille
        stats_section = QWidget()
        stats_layout = QGridLayout(stats_section)
        stats_layout.setHorizontalSpacing(20)
        stats_layout.setVerticalSpacing(20)

        try:
            total_eleves = self.count_table(Eleve)
            total_profs = self.count_table(Professeur)
            total_classes = self.count_table(Classe)
        except Exception as e:
            print(f"Erreur BD: {e}")
            total_eleves = "N/A"
            total_profs = "N/A"
            total_classes = "N/A"

        # Calculer le taux de remplissage
        try:
            taux_remplissage = self.calculer_taux_remplissage()
        except:
            taux_remplissage = "N/A"

        # Cartes de statistiques
        stats_cards = [
            ("Élèves inscrits", total_eleves, "#4070f4", "#e8eeff"),
            ("Professeurs", total_profs, "#ff6b6b", "#ffe8e8"),
            ("Classes actives", total_classes, "#4ecdc4", "#e8fcfb"),
            ("Taux de remplissage", f"{taux_remplissage}%", "#ffd166", "#fff9e6")
        ]

        for i, (title_text, value, color, bg_color) in enumerate(stats_cards):
            card = self.create_stat_card(title_text, value, color, bg_color)
            stats_layout.addWidget(card, i // 2, i % 2)

        layout.addWidget(stats_section)

        # Section graphique
        graph_section = QWidget()
        graph_layout = QVBoxLayout(graph_section)
        
        section_title = QLabel("Répartition par classe")
        section_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        section_title.setStyleSheet("color: #1e1f29; margin-bottom: 15px;")
        graph_layout.addWidget(section_title)

        graph_container = QFrame()
        graph_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                padding: 25px;
                border: none;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }
        """)
        graph_container_layout = QVBoxLayout(graph_container)
        
        try:
            graph = self.create_class_distribution_graph()
            graph.setMinimumHeight(400)
        except Exception as e:
            graph = QLabel(f"Erreur de chargement du graphique: {str(e)}")
            graph.setAlignment(Qt.AlignmentFlag.AlignCenter)
            graph.setStyleSheet("color: #ff6b6b; font-size: 14px; padding: 40px;")
        
        graph_container_layout.addWidget(graph)
        graph_layout.addWidget(graph_container)

        layout.addWidget(graph_section, 1)
        
        return page

    def create_stat_card(self, title, value, color, bg_color):
        frame = QFrame()
        frame.setMinimumSize(280, 140)
        frame.setMaximumSize(400, 160)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 20px;
                padding: 25px;
                border: none;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 white, stop:1 {bg_color});
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Ligne du haut : titre
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Medium))
        title_label.setStyleSheet(f"color: {color};")
        
        # Ligne du bas : valeur
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(value_label)

        return frame

    def count_table(self, model):
        try:
            session = SessionLocal()
            count = session.query(model).count()
            session.close()
            return count
        except Exception as e:
            print(f"Erreur comptage {model}: {e}")
            return "N/A"

    def calculer_taux_remplissage(self):
        """Calcule le taux de remplissage moyen des classes"""
        try:
            session = SessionLocal()
            
            # Supposons une capacité moyenne de 30 élèves par classe
            CAPACITE_MOYENNE = 30
            
            # Compter le nombre d'élèves par classe
            classes = session.query(Classe).all()
            total_taux = 0
            classes_avec_eleves = 0
            
            for classe in classes:
                nb_eleves = session.query(Eleve).filter(
                    Eleve.classe_actuelle_id == classe.id
                ).count()
                
                taux_classe = (nb_eleves / CAPACITE_MOYENNE) * 100
                if nb_eleves > 0:
                    total_taux += taux_classe
                    classes_avec_eleves += 1
            
            if classes_avec_eleves > 0:
                taux_moyen = total_taux / classes_avec_eleves
                return round(taux_moyen, 1)
            else:
                return 0
        except Exception as e:
            print(f"Erreur calcul taux remplissage: {e}")
            return "N/A"

    def create_class_distribution_graph(self):
        canvas = GraphCanvas()
        session = SessionLocal()
        
        try:
            classes = session.query(Classe).order_by(Classe.ordre).all()
            
            if not classes:
                ax = canvas.axes
                ax.clear()
                ax.text(0.5, 0.5, 'Aucune classe disponible', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12, color='gray')
                ax.set_xticks([])
                ax.set_yticks([])
                canvas.draw()
                return canvas
            
            x_labels = [c.nom for c in classes]
            y_eleves = []
            y_profs = []

            for classe in classes:
                # Compter les élèves actuellement dans cette classe
                nb_eleves = session.query(Eleve).filter(
                    Eleve.classe_actuelle_id == classe.id
                ).count()
                
                # Compter les professeurs actuellement dans cette classe
                nb_profs = session.query(Professeur).join(
                    professeur_classes
                ).filter(
                    professeur_classes.c.classe_id == classe.id
                ).count()
                
                y_eleves.append(nb_eleves)
                y_profs.append(nb_profs)

            ax = canvas.axes
            ax.clear()
            
            x = range(len(x_labels))
            width = 0.35
            
            bars1 = ax.bar([i - width/2 for i in x], y_eleves, width, 
                          label="Élèves", color="#4070f4", alpha=0.9, 
                          edgecolor='white', linewidth=1.5)
            bars2 = ax.bar([i + width/2 for i in x], y_profs, width, 
                          label="Professeurs", color="#ff6b6b", alpha=0.9, 
                          edgecolor='white', linewidth=1.5)
            
            ax.set_title("Répartition Élèves & Professeurs par Classe", 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel("Effectifs", fontsize=12, fontweight='medium')
            ax.set_xlabel("Classes", fontsize=12, fontweight='medium')
            
            ax.set_xticks(x)
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
            
            # Ajout des valeurs sur les barres
            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                           f'{int(height)}', ha='center', va='bottom', 
                           fontweight='bold', fontsize=9)
            
            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                           f'{int(height)}', ha='center', va='bottom', 
                           fontweight='bold', fontsize=9)
            
            # Style de la grille
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            ax.set_axisbelow(True)
            
            # Légende
            ax.legend(frameon=True, fancybox=True, shadow=True, 
                     loc='upper right', framealpha=0.9)
            
            # Enlever les bordures
            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
            
            # Ajuster les limites de l'axe Y pour mieux voir les données
            max_value = max(max(y_eleves) if y_eleves else 0, max(y_profs) if y_profs else 0)
            ax.set_ylim(0, max_value * 1.2 if max_value > 0 else 10)
            
            canvas.figure.tight_layout()

        except Exception as e:
            print(f"Erreur création graphique: {e}")
            ax = canvas.axes
            ax.clear()
            ax.text(0.5, 0.5, 'Erreur de chargement des données', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, color='red')
            ax.text(0.5, 0.4, f"Détail: {str(e)}", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=10, color='red')
            ax.set_xticks([])
            ax.set_yticks([])
        finally:
            session.close()

        canvas.draw()
        return canvas