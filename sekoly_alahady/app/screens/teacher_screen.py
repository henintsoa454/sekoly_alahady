from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox,
    QMessageBox, QDialog, QFormLayout, QDateEdit, QAbstractItemView,
    QListWidget, QListWidgetItem, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from app.databases.db import SessionLocal
from app.databases.models import Professeur, Classe, SexeEnum


class ProfesseurFormDialog(QDialog):
    """Dialogue pour ajouter/modifier un professeur"""
    def __init__(self, parent=None, professeur_id=None):
        super().__init__(parent)
        self.professeur_id = professeur_id
        self.setWindowTitle("Modifier le professeur" if professeur_id else "Ajouter un professeur")
        self.setFixedSize(450, 500)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulaire
        form_layout = QFormLayout()
        
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de famille")
        
        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Prénom")
        
        self.date_naissance = QDateEdit()
        self.date_naissance.setDate(QDate.currentDate().addYears(-30))
        self.date_naissance.setCalendarPopup(True)
        self.date_naissance.setMaximumDate(QDate.currentDate())
        
        self.sexe_combo = QComboBox()
        self.sexe_combo.addItem("Masculin", SexeEnum.MASCULIN)
        self.sexe_combo.addItem("Féminin", SexeEnum.FEMININ)
        
        # Sélection des classes (ListWidget pour sélection multiple)
        self.classes_label = QLabel("Classes enseignées:")
        self.classes_list = QListWidget()
        self.classes_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.classes_list.setFixedHeight(120)

        # Style des champs
        for widget in [self.nom_input, self.prenom_input, self.date_naissance, self.sexe_combo]:
            widget.setFixedHeight(40)
        
        # Style commun
        text_style = """
            QLineEdit, QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #4070f4;
                background-color: #f8fbff;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                selection-background-color: #4070f4;
                selection-color: white;
                font-size: 14px;
                color: #333333;
            }
        """
        
        list_style = """
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #333333;
            }
            QListWidget:focus {
                border-color: #4070f4;
                background-color: #f8fbff;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #4070f4;
                color: white;
            }
        """
        
        self.nom_input.setStyleSheet(text_style)
        self.prenom_input.setStyleSheet(text_style)
        self.date_naissance.setStyleSheet(text_style)
        self.sexe_combo.setStyleSheet(text_style)
        self.classes_list.setStyleSheet(list_style)

        form_layout.addRow("Nom:", self.nom_input)
        form_layout.addRow("Prénom:", self.prenom_input)
        form_layout.addRow("Date de naissance:", self.date_naissance)
        form_layout.addRow("Sexe:", self.sexe_combo)
        form_layout.addRow(self.classes_label)
        form_layout.addRow(self.classes_list)

        layout.addLayout(form_layout)

        # Boutons
        button_layout = QHBoxLayout()
        
        btn_save = QPushButton("Enregistrer")
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4070f4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3050c0;
            }
            QPushButton:pressed {
                background-color: #203090;
            }
        """)
        btn_save.clicked.connect(self.save_professeur)
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
            QPushButton:pressed {
                background-color: #3d4347;
            }
        """)
        btn_cancel.clicked.connect(self.reject)

        button_layout.addWidget(btn_cancel)
        button_layout.addStretch()
        button_layout.addWidget(btn_save)

        layout.addLayout(button_layout)

    def load_data(self):
        """Charge les données pour le formulaire"""
        session = SessionLocal()
        try:
            # Charger toutes les classes
            classes = session.query(Classe).order_by(Classe.ordre).all()
            self.classes_list.clear()
            
            for classe in classes:
                item = QListWidgetItem(classe.nom)
                item.setData(Qt.ItemDataRole.UserRole, classe.id)
                self.classes_list.addItem(item)
            
            # Charger les données du professeur si modification
            if self.professeur_id:
                professeur = session.query(Professeur).filter(Professeur.id == self.professeur_id).first()
                if professeur:
                    self.nom_input.setText(professeur.nom or "")
                    self.prenom_input.setText(professeur.prenom or "")
                    
                    # Date de naissance
                    if professeur.date_naissance:
                        date_qdate = QDate(professeur.date_naissance.year, 
                                          professeur.date_naissance.month, 
                                          professeur.date_naissance.day)
                        self.date_naissance.setDate(date_qdate)
                    
                    # Sexe
                    if professeur.sexe:
                        for i in range(self.sexe_combo.count()):
                            if self.sexe_combo.itemData(i) == professeur.sexe:
                                self.sexe_combo.setCurrentIndex(i)
                                break
                    
                    # Sélectionner les classes enseignées
                    if professeur.classes_actuelles:
                        for classe in professeur.classes_actuelles:
                            for i in range(self.classes_list.count()):
                                item = self.classes_list.item(i)
                                if item.data(Qt.ItemDataRole.UserRole) == classe.id:
                                    item.setSelected(True)
                                    break
        finally:
            session.close()

    def save_professeur(self):
        """Sauvegarde le professeur selon le modèle actuel"""
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        date_naissance = self.date_naissance.date().toPyDate()
        sexe = self.sexe_combo.currentData()

        if not nom or not prenom:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir le nom et prénom")
            return

        session = SessionLocal()
        try:
            if self.professeur_id:
                # Modification
                professeur = session.query(Professeur).filter(Professeur.id == self.professeur_id).first()
                if professeur:
                    professeur.nom = nom
                    professeur.prenom = prenom
                    professeur.date_naissance = date_naissance
                    professeur.sexe = sexe
                    
                    # Mettre à jour les classes
                    professeur.classes_actuelles.clear()
                    for i in range(self.classes_list.count()):
                        item = self.classes_list.item(i)
                        if item.isSelected():
                            classe_id = item.data(Qt.ItemDataRole.UserRole)
                            classe = session.query(Classe).filter(Classe.id == classe_id).first()
                            if classe:
                                professeur.classes_actuelles.append(classe)
                    
                    message = "Professeur modifié avec succès!"
            else:
                # Ajout
                nouveau_professeur = Professeur(
                    nom=nom,
                    prenom=prenom,
                    date_naissance=date_naissance,
                    sexe=sexe,
                )
                
                # Ajouter les classes sélectionnées
                for i in range(self.classes_list.count()):
                    item = self.classes_list.item(i)
                    if item.isSelected():
                        classe_id = item.data(Qt.ItemDataRole.UserRole)
                        classe = session.query(Classe).filter(Classe.id == classe_id).first()
                        if classe:
                            nouveau_professeur.classes_actuelles.append(classe)
                
                session.add(nouveau_professeur)
                message = "Professeur ajouté avec succès!"

            session.commit()
            QMessageBox.information(self, "Succès", message)
            self.accept()

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
        finally:
            session.close()


class TeacherScreen(QWidget):
    """Page principale de gestion des professeurs"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_professeurs()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # En-tête
        header_layout = QHBoxLayout()
        
        title = QLabel("Gestion des Professeurs")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e1f29; margin-bottom: 5px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Bouton d'ajout
        self.btn_add = QPushButton("Ajouter un professeur")
        self.btn_add.setFixedHeight(45)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4070f4;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0px 25px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3050c0;
            }
            QPushButton:pressed {
                background-color: #203090;
            }
        """)
        self.btn_add.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(self.btn_add)

        main_layout.addLayout(header_layout)

        # Barre de recherche et filtres
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un professeur par nom ou prénom...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self.filter_professeurs)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #4070f4;
                background-color: #f8fbff;
            }
        """)
        
        self.sexe_filter = QComboBox()
        self.sexe_filter.setFixedHeight(40)
        self.sexe_filter.addItem("Tous les sexes", None)
        self.sexe_filter.addItem("Masculin", SexeEnum.MASCULIN)
        self.sexe_filter.addItem("Féminin", SexeEnum.FEMININ)
        self.sexe_filter.currentIndexChanged.connect(self.filter_professeurs)
        
        self.classe_filter = QComboBox()
        self.classe_filter.setFixedHeight(40)
        self.classe_filter.addItem("Toutes les classes", None)
        self.classe_filter.currentIndexChanged.connect(self.filter_professeurs)
        
        combo_style = """
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #333333;
                min-width: 150px;
            }
            QComboBox:focus {
                border-color: #4070f4;
                background-color: #f8fbff;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                selection-background-color: #4070f4;
                selection-color: white;
                font-size: 14px;
                color: #333333;
                padding: 5px;
            }
        """
        
        self.sexe_filter.setStyleSheet(combo_style)
        self.classe_filter.setStyleSheet(combo_style)

        filter_layout.addWidget(self.search_input, 3)
        filter_layout.addWidget(QLabel("Sexe:"))
        filter_layout.addWidget(self.sexe_filter, 1)
        filter_layout.addWidget(QLabel("Classe:"))
        filter_layout.addWidget(self.classe_filter, 1)

        main_layout.addWidget(filter_frame)

        # Tableau des professeurs
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        table_container_layout = QVBoxLayout(table_container)
        table_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tableau des professeurs selon le modèle actuel
        self.table_professeurs = QTableWidget()
        self.table_professeurs.setColumnCount(7)  # Colonnes selon le modèle
        self.table_professeurs.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Date Naissance", "Sexe", "Classes", "Actions"
        ])
        
        # Configuration des largeurs de colonnes
        header = self.table_professeurs.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)   # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nom
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Prénom
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)   # Date Naissance
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)   # Sexe
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)   # Classes
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)   # Actions
        
        self.table_professeurs.setColumnWidth(0, 50)   # ID
        self.table_professeurs.setColumnWidth(3, 120)  # Date Naissance
        self.table_professeurs.setColumnWidth(4, 80)   # Sexe
        self.table_professeurs.setColumnWidth(5, 150)  # Classes
        self.table_professeurs.setColumnWidth(6, 180)  # Actions
        
        self.table_professeurs.verticalHeader().setDefaultSectionSize(55)
        self.table_professeurs.verticalHeader().setVisible(False)
        
        # Style du tableau
        self.table_professeurs.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #f0f0f0;
                alternate-background-color: #f9f9f9;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #f0f0f0;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1e1f29;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px 8px;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 2px solid #4070f4;
                font-weight: bold;
                font-size: 13px;
                color: #1e1f29;
                text-align: center;
            }
        """)
        
        self.table_professeurs.setAlternatingRowColors(True)
        self.table_professeurs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_professeurs.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        table_container_layout.addWidget(self.table_professeurs)
        main_layout.addWidget(table_container, 1)

        # Statistiques
        self.stats_label = QLabel("Chargement des données...")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 15px;
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                font-weight: 500;
            }
        """)
        main_layout.addWidget(self.stats_label)

        # Charger les filtres
        self.load_filters()

    def load_filters(self):
        """Charge les classes dans le filtre"""
        session = SessionLocal()
        try:
            classes = session.query(Classe).order_by(Classe.ordre).all()
            for classe in classes:
                self.classe_filter.addItem(classe.nom, classe.id)
        finally:
            session.close()

    def load_professeurs(self):
        """Charge la liste des professeurs"""
        session = SessionLocal()
        try:
            professeurs = session.query(Professeur).order_by(Professeur.nom, Professeur.prenom).all()
            
            self.table_professeurs.setRowCount(0)
            
            if not professeurs:
                self.table_professeurs.setRowCount(1)
                self.table_professeurs.setItem(0, 0, QTableWidgetItem("Aucun professeur enregistré"))
                self.table_professeurs.setSpan(0, 0, 1, 7)
                self.table_professeurs.item(0, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_professeurs.item(0, 0).setFont(QFont("Segoe UI", 12))
                self.table_professeurs.item(0, 0).setForeground(QColor("#666666"))
                self.stats_label.setText(" Aucun professeur enregistré")
                return
            
            self.table_professeurs.setRowCount(len(professeurs))
            
            # Mapping pour l'affichage du sexe
            sexe_display = {
                SexeEnum.MASCULIN: "Masculin",
                SexeEnum.FEMININ: "Féminin",
            }
            
            for row, professeur in enumerate(professeurs):
                self.table_professeurs.setRowHeight(row, 55)
                
                # ID
                item_id = QTableWidgetItem(str(professeur.id))
                item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_professeurs.setItem(row, 0, item_id)
                
                # Nom (en majuscules)
                item_nom = QTableWidgetItem(professeur.nom.upper() if professeur.nom else "")
                item_nom.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                self.table_professeurs.setItem(row, 1, item_nom)
                
                # Prénom
                item_prenom = QTableWidgetItem(professeur.prenom or "")
                item_prenom.setFont(QFont("Segoe UI", 12))
                self.table_professeurs.setItem(row, 2, item_prenom)
                
                # Date de naissance
                date_naissance_str = professeur.date_naissance.strftime("%d/%m/%Y") if professeur.date_naissance else ""
                item_date_naissance = QTableWidgetItem(date_naissance_str)
                item_date_naissance.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_date_naissance.setFont(QFont("Segoe UI", 11))
                item_date_naissance.setForeground(QColor("#666666"))
                self.table_professeurs.setItem(row, 3, item_date_naissance)
                
                # Sexe
                sexe_text = sexe_display.get(professeur.sexe, "")
                item_sexe = QTableWidgetItem(sexe_text)
                item_sexe.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_sexe.setFont(QFont("Segoe UI", 11))
                
                # Couleur différente selon le sexe
                if professeur.sexe == SexeEnum.MASCULIN:
                    item_sexe.setForeground(QColor("#2196F3"))
                elif professeur.sexe == SexeEnum.FEMININ:
                    item_sexe.setForeground(QColor("#E91E63"))
                
                self.table_professeurs.setItem(row, 4, item_sexe)
                
                # Classes enseignées
                classes_names = [classe.nom for classe in professeur.classes_actuelles]
                classes_text = ", ".join(classes_names) if classes_names else "Aucune"
                item_classes = QTableWidgetItem(classes_text)
                item_classes.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_classes.setFont(QFont("Segoe UI", 11))
                item_classes.setForeground(QColor("#4CAF50"))
                self.table_professeurs.setItem(row, 5, item_classes)
                
                # Actions
                actions_widget = QWidget()
                actions_widget.setFixedHeight(45)
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                actions_layout.setSpacing(8)
                
                # Bouton Modifier
                btn_edit = QPushButton("Modifier")
                btn_edit.setToolTip("Modifier ce professeur")
                btn_edit.setFixedSize(85, 35)
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #ffc107;
                        color: #333333;
                        border: none;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e0a800;
                        color: white;
                    }
                    QPushButton:pressed {
                        background-color: #c69500;
                    }
                """)
                btn_edit.clicked.connect(lambda checked, pid=professeur.id: self.show_edit_dialog(pid))
                
                # Bouton Supprimer
                btn_delete = QPushButton("Supprimer")
                btn_delete.setToolTip("Supprimer ce professeur")
                btn_delete.setFixedSize(85, 35)
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                    QPushButton:pressed {
                        background-color: #a71d2a;
                    }
                """)
                btn_delete.clicked.connect(lambda checked, pid=professeur.id: self.delete_professeur(pid))
                
                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)
                actions_layout.addStretch()
                
                self.table_professeurs.setCellWidget(row, 6, actions_widget)
            
            # Mettre à jour les statistiques
            self.update_stats()
            
        except Exception as e:
            print(f"Erreur lors du chargement des professeurs: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")
        finally:
            session.close()

    def filter_professeurs(self):
        """Filtre les professeurs selon les critères"""
        search_text = self.search_input.text().lower()
        sexe = self.sexe_filter.currentData()
        classe_id = self.classe_filter.currentData()
        
        rows_visible = 0
        
        for row in range(self.table_professeurs.rowCount()):
            item = self.table_professeurs.item(row, 0)
            if item and item.text() == "Aucun professeur enregistré":
                continue
                
            nom_item = self.table_professeurs.item(row, 1)
            prenom_item = self.table_professeurs.item(row, 2)
            sexe_item = self.table_professeurs.item(row, 4)
            classes_item = self.table_professeurs.item(row, 5)
            
            if nom_item and prenom_item:
                nom = nom_item.text().lower()
                prenom = prenom_item.text().lower()
                
                # Filtre de recherche
                search_match = search_text in nom or search_text in prenom
                
                # Filtre de sexe
                if sexe:
                    if sexe_item:
                        sexe_text = sexe_item.text()
                        if sexe == SexeEnum.MASCULIN and "Masculin" in sexe_text:
                            sexe_match = True
                        elif sexe == SexeEnum.FEMININ and "Féminin" in sexe_text:
                            sexe_match = True
                        else:
                            sexe_match = False
                    else:
                        sexe_match = False
                else:
                    sexe_match = True
                
                # Filtre de classe
                if classe_id:
                    if classes_item:
                        classes_text = classes_item.text()
                        classe_nom = self.classe_filter.currentText()
                        # Vérifier si le nom de la classe est dans la liste des classes du professeur
                        classe_match = classe_nom in classes_text
                    else:
                        classe_match = False
                else:
                    classe_match = True
                
                visible = search_match and sexe_match and classe_match
                self.table_professeurs.setRowHidden(row, not visible)
                
                if visible:
                    rows_visible += 1
        
        if rows_visible > 0:
            self.stats_label.setText(f"Affichage de {rows_visible} professeur(s)")

    def update_stats(self):
        """Met à jour les statistiques"""
        session = SessionLocal()
        try:
            total_professeurs = session.query(Professeur).count()
            
            if total_professeurs == 0:
                self.stats_label.setText(" Aucun professeur enregistré")
                return
            
            # Compter par sexe
            masculin = session.query(Professeur).filter(Professeur.sexe == SexeEnum.MASCULIN).count()
            feminin = session.query(Professeur).filter(Professeur.sexe == SexeEnum.FEMININ).count()
            
            # Compter les professeurs sans classe
            professeurs_sans_classe = session.query(Professeur).filter(~Professeur.classes_actuelles.any()).count()
            
            stats_text = f"Total: {total_professeurs} professeur(s) | Masculin: {masculin} | Féminin: {feminin} | Sans classe: {professeurs_sans_classe}"
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            print(f"Erreur dans update_stats: {e}")
            self.stats_label.setText("Erreur de chargement des statistiques")
        finally:
            session.close()

    def show_add_dialog(self):
        """Affiche le dialogue d'ajout"""
        dialog = ProfesseurFormDialog(self)
        if dialog.exec():
            print("Professeur ajouté, rechargement des données...")
            self.load_professeurs()

    def show_edit_dialog(self, professeur_id):
        """Affiche le dialogue de modification"""
        dialog = ProfesseurFormDialog(self, professeur_id)
        if dialog.exec():
            print("Professeur modifié, rechargement des données...")
            self.load_professeurs()

    def delete_professeur(self, professeur_id):
        """Supprime un professeur"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce professeur ?\n\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = SessionLocal()
            try:
                professeur = session.query(Professeur).filter(Professeur.id == professeur_id).first()
                if professeur:
                    session.delete(professeur)
                    session.commit()
                    QMessageBox.information(self, "Succès", "Professeur supprimé avec succès!")
                    print("Professeur supprimé, rechargement des données...")
                    self.load_professeurs()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
            finally:
                session.close()