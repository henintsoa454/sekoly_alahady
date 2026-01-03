from sqlalchemy import text
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox,
    QMessageBox, QDialog, QFormLayout, QDateEdit, QAbstractItemView,
    QTabWidget, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from app.databases.db import SessionLocal
from app.databases.models import Eleve, Classe, SexeEnum, eleve_classe_historique
from app.utils.dynamic_tables import (
    setup_dynamic_table, get_dynamic_columns, get_value_from_model, get_column_display_name
)


class EleveFormDialog(QDialog):
    """Dialogue pour ajouter/modifier un élève"""
    def __init__(self, parent=None, eleve_id=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.setWindowTitle("Modifier l'élève" if eleve_id else "Ajouter un élève")
        self.setFixedSize(500, 450)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Onglets pour le formulaire et l'historique
        self.tab_widget = QTabWidget()
        
        # Onglet 1: Informations de base
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        
        # Formulaire
        form_layout = QFormLayout()
        
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de famille")
        
        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Prénom")
        
        self.classe_combo = QComboBox()
        
        self.date_naissance = QDateEdit()
        self.date_naissance.setDate(QDate.currentDate().addYears(-10))
        self.date_naissance.setCalendarPopup(True)
        self.date_naissance.setMaximumDate(QDate.currentDate())
        
        self.sexe_combo = QComboBox()
        self.sexe_combo.addItem("Masculin", SexeEnum.MASCULIN)
        self.sexe_combo.addItem("Féminin", SexeEnum.FEMININ)

        # Champ : contact_parent
        self.contact_parent_input = QLineEdit()
        self.contact_parent_input.setPlaceholderText("+243 XX XX XX XX")
        self.contact_parent_input.setMaxLength(20)

        # Style des champs
        for widget in [self.nom_input, self.prenom_input, self.classe_combo, 
                      self.date_naissance, self.sexe_combo, self.contact_parent_input]:
            widget.setFixedHeight(40)
        
        # Style pour les champs de texte
        text_style = """
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #4070f4;
                background-color: #f8fbff;
            }
        """
        
        # Style pour les combobox
        combo_style = """
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #333333;
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
            }
        """
        
        self.nom_input.setStyleSheet(text_style)
        self.prenom_input.setStyleSheet(text_style)
        self.classe_combo.setStyleSheet(combo_style)
        self.date_naissance.setStyleSheet(text_style)
        self.sexe_combo.setStyleSheet(combo_style)
        self.contact_parent_input.setStyleSheet(text_style)

        form_layout.addRow("Nom:", self.nom_input)
        form_layout.addRow("Prénom:", self.prenom_input)
        form_layout.addRow("Classe actuelle:", self.classe_combo)
        form_layout.addRow("Date de naissance:", self.date_naissance)
        form_layout.addRow("Sexe:", self.sexe_combo)
        form_layout.addRow("Contact parent:", self.contact_parent_input)

        info_layout.addLayout(form_layout)
        info_layout.addStretch()
        
        # Onglet 2: Historique des classes (uniquement en mode modification)
        if self.eleve_id:
            historique_tab = QWidget()
            historique_layout = QVBoxLayout(historique_tab)
            
            self.historique_table = QTableWidget()
            self.historique_table.setColumnCount(3)
            self.historique_table.setHorizontalHeaderLabels(["Classe", "Date début", "Date fin"])
            
            # Configuration du tableau d'historique
            header = self.historique_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            self.historique_table.setColumnWidth(1, 120)
            self.historique_table.setColumnWidth(2, 120)
            
            self.historique_table.verticalHeader().setVisible(False)
            self.historique_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            
            historique_layout.addWidget(self.historique_table)
            
            self.tab_widget.addTab(info_tab, "Informations")
            self.tab_widget.addTab(historique_tab, "Historique des classes")
        else:
            self.tab_widget.addTab(info_tab, "Informations")
        
        layout.addWidget(self.tab_widget)

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
        btn_save.clicked.connect(self.save_eleve)
        
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
        """Charge les classes et les données de l'élève si modification"""
        session = SessionLocal()
        try:
            # Charger les classes
            classes = session.query(Classe).order_by(Classe.ordre).all()
            self.classe_combo.clear()
            for classe in classes:
                self.classe_combo.addItem(classe.nom, classe.id)
            
            # Charger les données de l'élève si modification
            if self.eleve_id:
                eleve = session.query(Eleve).filter(Eleve.id == self.eleve_id).first()
                if eleve:
                    self.nom_input.setText(eleve.nom or "")
                    self.prenom_input.setText(eleve.prenom or "")
                    
                    # Conversion de la date de naissance Python en QDate
                    if eleve.date_naissance:
                        date_qdate = QDate(eleve.date_naissance.year, 
                                          eleve.date_naissance.month, 
                                          eleve.date_naissance.day)
                        self.date_naissance.setDate(date_qdate)
                    
                    # Sélectionner la bonne classe
                    if eleve.classe_actuelle_id:
                        index = self.classe_combo.findData(eleve.classe_actuelle_id)
                        if index >= 0:
                            self.classe_combo.setCurrentIndex(index)
                    
                    # Sélectionner le sexe
                    if eleve.sexe:
                        for i in range(self.sexe_combo.count()):
                            if self.sexe_combo.itemData(i) == eleve.sexe:
                                self.sexe_combo.setCurrentIndex(i)
                                break
                    
                    # Charger le contact parent
                    if hasattr(eleve, 'contact_parent'):
                        self.contact_parent_input.setText(eleve.contact_parent or "")
                    
                    # Charger l'historique des classes
                    self.load_historique_classes(session, eleve)
        finally:
            session.close()

    def load_historique_classes(self, session, eleve):
        """Charge l'historique des classes de l'élève"""
        if hasattr(self, 'historique_table'):
            # Récupérer l'historique des classes depuis la table d'association
            historique_query = session.execute(
                text("""
                    SELECT c.nom, h.date_debut, h.date_fin
                    FROM eleve_classe_historique h
                    JOIN classes c ON h.classe_id = c.id
                    WHERE h.eleve_id = :eleve_id
                    ORDER BY h.date_debut DESC
                """),
                {"eleve_id": eleve.id}
            )
            
            historiques = historique_query.fetchall()
            
            self.historique_table.setRowCount(len(historiques))
            
            for row, (classe_nom, date_debut, date_fin) in enumerate(historiques):
                # Classe
                item_classe = QTableWidgetItem(classe_nom)
                self.historique_table.setItem(row, 0, item_classe)
                
                # Date début
                date_debut_str = date_debut.strftime("%d/%m/%Y %H:%M") if date_debut else ""
                item_debut = QTableWidgetItem(date_debut_str)
                self.historique_table.setItem(row, 1, item_debut)
                
                # Date fin
                date_fin_str = date_fin.strftime("%d/%m/%Y %H:%M") if date_fin else "Actuelle"
                item_fin = QTableWidgetItem(date_fin_str)
                if date_fin is None:
                    item_fin.setForeground(QColor("#4CAF50"))
                self.historique_table.setItem(row, 2, item_fin)

    def save_eleve(self):
        """Sauvegarde l'élève selon le modèle actuel"""
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        classe_id = self.classe_combo.currentData()
        date_naissance = self.date_naissance.date().toPyDate()
        sexe = self.sexe_combo.currentData()
        contact_parent = self.contact_parent_input.text().strip() or None

        # Validation
        if not nom or not prenom:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir le nom et le prénom")
            return

        if not date_naissance:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une date de naissance")
            return

        # Validation du contact parent (max 20 caractères)
        if contact_parent and len(contact_parent) > 20:
            QMessageBox.warning(self, "Erreur", 
                              "Le contact parent ne doit pas dépasser 20 caractères")
            return

        session = SessionLocal()
        try:
            if self.eleve_id:
                # Modification - Vérifier si la classe a changé
                eleve = session.query(Eleve).filter(Eleve.id == self.eleve_id).first()
                if eleve:
                    # Vérifier si la classe a changé
                    classe_ancienne_id = eleve.classe_actuelle_id
                    
                    # Mettre à jour les informations de l'élève
                    eleve.nom = nom
                    eleve.prenom = prenom
                    eleve.classe_actuelle_id = classe_id
                    eleve.date_naissance = date_naissance
                    eleve.sexe = sexe
                    
                    # Mettre à jour le contact parent
                    if hasattr(eleve, 'contact_parent'):
                        eleve.contact_parent = contact_parent
                    
                    # Si la classe a changé, mettre à jour l'historique
                    if classe_ancienne_id and classe_ancienne_id != classe_id:
                        # Mettre à jour la date de fin pour l'ancienne classe dans l'historique
                        session.execute(
                            text("""
                                UPDATE eleve_classe_historique
                                SET date_fin = CURRENT_TIMESTAMP
                                WHERE eleve_id = :eleve_id 
                                AND classe_id = :classe_id 
                                AND date_fin IS NULL
                            """),
                            {"eleve_id": eleve.id, "classe_id": classe_ancienne_id}
                        )
                        
                        # Ajouter la nouvelle entrée dans l'historique
                        session.execute(
                            text("""
                                INSERT INTO eleve_classe_historique (eleve_id, classe_id, date_debut)
                                VALUES (:eleve_id, :classe_id, CURRENT_TIMESTAMP)
                            """),
                            {"eleve_id": eleve.id, "classe_id": classe_id}
                        )
                    
                    message = "Élève modifié avec succès!"
            else:
                # Ajout d'un nouvel élève
                nouvel_eleve = Eleve(
                    nom=nom,
                    prenom=prenom,
                    classe_actuelle_id=classe_id,
                    date_naissance=date_naissance,
                    sexe=sexe,
                )
                
                # Ajouter le contact parent
                if hasattr(nouvel_eleve, 'contact_parent'):
                    nouvel_eleve.contact_parent = contact_parent
                
                session.add(nouvel_eleve)
                session.flush()  # Pour obtenir l'ID de l'élève
                
                # Ajouter l'entrée initiale dans l'historique des classes
                session.execute(
                    text("""
                        INSERT INTO eleve_classe_historique (eleve_id, classe_id, date_debut)
                        VALUES (:eleve_id, :classe_id, CURRENT_TIMESTAMP)
                    """),
                    {"eleve_id": nouvel_eleve.id, "classe_id": classe_id}
                )
                
                message = "Élève ajouté avec succès!"

            session.commit()
            QMessageBox.information(self, "Succès", message)
            self.accept()

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
        finally:
            session.close()


class StudentScreen(QWidget):
    """Page principale de gestion des élèves"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_eleves()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # En-tête
        header_layout = QHBoxLayout()
        
        title = QLabel("Gestion des Élèves")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e1f29; margin-bottom: 5px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Boutons d'actions
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        # Bouton d'ajout
        self.btn_add = QPushButton("Ajouter un élève")
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
        
        # Bouton d'historique (visible uniquement lorsqu'un élève est sélectionné)
        self.btn_historique = QPushButton("Historique")
        self.btn_historique.setFixedHeight(45)
        self.btn_historique.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0px 25px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
            QPushButton:pressed {
                background-color: #3d4347;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #999;
            }
        """)
        self.btn_historique.setEnabled(False)
        self.btn_historique.clicked.connect(self.show_historique_dialog)
        
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_historique)
        
        header_layout.addWidget(button_container)
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
        self.search_input.setPlaceholderText("Rechercher un élève par nom ou prénom...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self.filter_eleves)
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
        
        self.classe_filter = QComboBox()
        self.classe_filter.setFixedHeight(40)
        self.classe_filter.addItem("Toutes les classes", None)
        self.classe_filter.currentIndexChanged.connect(self.filter_eleves)
        
        self.sexe_filter = QComboBox()
        self.sexe_filter.setFixedHeight(40)
        self.sexe_filter.addItem("Tous les sexes", None)
        self.sexe_filter.addItem("Masculin", SexeEnum.MASCULIN)
        self.sexe_filter.addItem("Féminin", SexeEnum.FEMININ)
        self.sexe_filter.currentIndexChanged.connect(self.filter_eleves)

        combo_style = """
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #333333;
                min-width: 180px;
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
        
        self.classe_filter.setStyleSheet(combo_style)
        self.sexe_filter.setStyleSheet(combo_style)

        filter_layout.addWidget(self.search_input, 3)
        filter_layout.addWidget(QLabel("Classe:"))
        filter_layout.addWidget(self.classe_filter, 1)
        filter_layout.addWidget(QLabel("Sexe:"))
        filter_layout.addWidget(self.sexe_filter, 1)

        main_layout.addWidget(filter_frame)

        # Tableau des élèves
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
        
        self.table_eleves = QTableWidget()
        
        # Configuration dynamique des colonnes
        self.eleve_columns = get_dynamic_columns("Eleve", include_base=True)
        if "classe_actuelle_id" in self.eleve_columns:
            self.eleve_columns.remove("classe_actuelle_id")
        
        # Créer la liste des colonnes d'affichage avec "Classe" insérée
        display_columns = self.eleve_columns.copy()
        if "prenom" in display_columns:
            prénom_idx = display_columns.index("prenom")
            display_columns.insert(prénom_idx + 1, "classe_display")
        
        # Configurer le tableau
        self.table_eleves.setColumnCount(len(display_columns) + 1)  # +1 pour Actions
        
        # En-têtes
        headers = []
        for col in display_columns:
            if col == "classe_display":
                headers.append("Classe")
            else:
                headers.append(get_column_display_name("Eleve", col))
        headers.append("Actions")
        self.table_eleves.setHorizontalHeaderLabels(headers)
        
        # Configuration des colonnes
        header = self.table_eleves.horizontalHeader()
        for i, col in enumerate(display_columns):
            if col == "id":
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                self.table_eleves.setColumnWidth(i, 60)
            elif col in ["nom", "prenom"]:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            elif col == "classe_display":
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                self.table_eleves.setColumnWidth(i, 100)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                self.table_eleves.setColumnWidth(i, 120)
        
        # Colonne Actions
        actions_col = len(display_columns)
        header.setSectionResizeMode(actions_col, QHeaderView.ResizeMode.Fixed)
        self.table_eleves.setColumnWidth(actions_col, 180)
        
        # Hauteur des lignes et sélection
        self.table_eleves.verticalHeader().setDefaultSectionSize(50)
        self.table_eleves.verticalHeader().setVisible(False)
        self.table_eleves.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_eleves.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Style du tableau
        self.table_eleves.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #f0f0f0;
                alternate-background-color: #f9f9f9;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px 5px;
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
                padding: 10px 5px;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 2px solid #4070f4;
                font-weight: bold;
                font-size: 12px;
                color: #1e1f29;
                text-align: center;
            }
        """)
        
        self.table_eleves.setAlternatingRowColors(True)
        self.table_eleves.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        table_container_layout.addWidget(self.table_eleves)
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

    def load_eleves(self):
        """Charge la liste des élèves"""
        session = SessionLocal()
        try:
            eleves = session.query(Eleve).join(Classe, Eleve.classe_actuelle_id == Classe.id).order_by(Eleve.nom, Eleve.prenom).all()
            
            self.table_eleves.setRowCount(0)
            
            # Recharger les colonnes dynamiques
            self.eleve_columns = get_dynamic_columns("Eleve", include_base=True)
            if "classe_actuelle_id" in self.eleve_columns:
                self.eleve_columns.remove("classe_actuelle_id")
            
            # Créer la liste des colonnes d'affichage avec "Classe" insérée
            display_columns = self.eleve_columns.copy()
            if "prenom" in display_columns:
                prénom_idx = display_columns.index("prenom")
                display_columns.insert(prénom_idx + 1, "classe_display")
            
            if not eleves:
                self.table_eleves.setRowCount(1)
                total_cols = len(display_columns) + 1  # +1 pour Actions
                self.table_eleves.setItem(0, 0, QTableWidgetItem("Aucun élève enregistré"))
                self.table_eleves.setSpan(0, 0, 1, total_cols)
                self.table_eleves.item(0, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_eleves.item(0, 0).setFont(QFont("Segoe UI", 12))
                self.table_eleves.item(0, 0).setForeground(QColor("#666666"))
                self.stats_label.setText(" Aucun élève enregistré")
                return
            
            self.table_eleves.setRowCount(len(eleves))
            
            # Mapping pour l'affichage du sexe
            sexe_display = {
                SexeEnum.MASCULIN: "M",
                SexeEnum.FEMININ: "F",
            }
            
            # Recharger les colonnes dynamiques
            self.eleve_columns = get_dynamic_columns("Eleve", include_base=True)
            # Exclure classe_actuelle_id car on affichera "Classe" à la place
            if "classe_actuelle_id" in self.eleve_columns:
                self.eleve_columns.remove("classe_actuelle_id")
            
            # Ajouter "Classe" comme colonne spéciale
            display_columns = self.eleve_columns.copy()
            if "nom" in display_columns and "prenom" in display_columns:
                # Insérer "Classe" après prénom
                prénom_idx = display_columns.index("prenom")
                display_columns.insert(prénom_idx + 1, "classe_display")
            
            for row, eleve in enumerate(eleves):
                self.table_eleves.setRowHeight(row, 50)
                
                col_idx = 0
                for col_name in display_columns:
                    if col_name == "classe_display":
                        # Colonne spéciale pour afficher la classe
                        classe_name = eleve.classe_actuelle.nom if eleve.classe_actuelle else "N/A"
                        item = QTableWidgetItem(classe_name)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
                        item.setForeground(QColor("#4070f4"))
                    elif col_name == "sexe":
                        # Formatage spécial pour le sexe
                        sexe_text = sexe_display.get(eleve.sexe, "")
                        item = QTableWidgetItem(sexe_text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item.setFont(QFont("Segoe UI", 11))
                        if eleve.sexe == SexeEnum.MASCULIN:
                            item.setForeground(QColor("#2196F3"))
                        elif eleve.sexe == SexeEnum.FEMININ:
                            item.setForeground(QColor("#E91E63"))
                    elif col_name == "nom":
                        # Nom en majuscules et gras
                        item = QTableWidgetItem(eleve.nom.upper() if eleve.nom else "")
                        item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                    elif col_name == "date_naissance":
                        # Formatage de date
                        date_str = eleve.date_naissance.strftime("%d/%m/%Y") if eleve.date_naissance else ""
                        item = QTableWidgetItem(date_str)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item.setFont(QFont("Segoe UI", 10))
                        item.setForeground(QColor("#666666"))
                    elif col_name == "contact_parent":
                        # Formatage spécial pour contact
                        contact = getattr(eleve, 'contact_parent', '') or ""
                        item = QTableWidgetItem(contact)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item.setFont(QFont("Segoe UI", 10))
                        item.setForeground(QColor("#4CAF50"))
                    else:
                        # Colonnes dynamiques ou autres colonnes de base
                        value = get_value_from_model(eleve, col_name, "Eleve")
                        item = QTableWidgetItem(value)
                        if col_name == "id":
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            item.setFont(QFont("Segoe UI", 10))
                    
                    self.table_eleves.setItem(row, col_idx, item)
                    col_idx += 1
                
                # Actions (dernière colonne)
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 10, 5, 10)
                actions_layout.setSpacing(5)
                
                actions_widget.setFixedHeight(50)
                
                # Bouton Modifier
                btn_edit = QPushButton("Modifier")
                btn_edit.setToolTip("Modifier cet élève")
                btn_edit.setFixedSize(85, 35)
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #ffc107;
                        color: #333333;
                        border: none;
                        border-radius: 6px;
                        font-size: 11px;
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
                btn_edit.clicked.connect(lambda checked, eid=eleve.id: self.show_edit_dialog(eid))
                
                # Bouton Supprimer
                btn_delete = QPushButton("Supprimer")
                btn_delete.setToolTip("Supprimer cet élève")
                btn_delete.setFixedSize(85, 35)
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                    QPushButton:pressed {
                        background-color: #a71d2a;
                    }
                """)
                btn_delete.clicked.connect(lambda checked, eid=eleve.id: self.delete_eleve(eid))
                
                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)
                actions_layout.addStretch()
                
                actions_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
                
                self.table_eleves.setCellWidget(row, col_idx, actions_widget)
            
            # Mettre à jour les statistiques
            self.update_stats()
            
        except Exception as e:
            print(f"Erreur lors du chargement des élèves: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")
        finally:
            session.close()

    def get_notes_by_classe(self, session, eleve_id, classe_id):
        """Récupère les notes de l'élève pour une classe donnée"""
        try:
            # Supposons que vous avez une table notes avec une relation à Eleve et Matiere
            # Cette requête peut varier selon votre modèle de données
            notes_query = session.execute(
                text("""
                    SELECT 
                        m.nom as matiere,
                        n.valeur as note,
                        n.coefficient as coefficient,
                        n.date_note as date_note
                    FROM notes n
                    JOIN matieres m ON n.matiere_id = m.id
                    WHERE n.eleve_id = :eleve_id 
                    AND m.classe_id = :classe_id
                    ORDER BY m.nom
                """),
                {"eleve_id": eleve_id, "classe_id": classe_id}
            )
            return notes_query.fetchall()
        except Exception as e:
            print(f"Erreur lors de la récupération des notes: {e}")
            return []

    def on_selection_changed(self):
        """Active/désactive le bouton d'historique selon la sélection"""
        selected_rows = self.table_eleves.selectionModel().selectedRows()
        self.btn_historique.setEnabled(len(selected_rows) == 1)

    def show_historique_dialog(self):
        """Affiche le dialogue d'historique complet avec notes"""
        selected_rows = self.table_eleves.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        eleve_id = int(self.table_eleves.item(row, 0).text())
        
        # Créer un dialogue pour afficher l'historique complet
        dialog = QDialog(self)
        dialog.setWindowTitle("Historique complet de l'élève")
        dialog.setFixedSize(900, 600)  # Augmenté la taille pour les notes
        
        layout = QVBoxLayout(dialog)
        
        # Récupérer les informations de l'élève
        session = SessionLocal()
        try:
            eleve = session.query(Eleve).filter(Eleve.id == eleve_id).first()
            if not eleve:
                return
            
            # Informations de l'élève
            info_group = QGroupBox(f"{eleve.nom.upper()} {eleve.prenom}")
            info_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    font-size: 14px;
                    border: 2px solid #4070f4;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 15px;
                }
            """)
            info_layout = QGridLayout()
            
            info_layout.addWidget(QLabel("Classe actuelle:"), 0, 0)
            info_layout.addWidget(QLabel(eleve.classe_actuelle.nom if eleve.classe_actuelle else "N/A"), 0, 1)
            
            info_layout.addWidget(QLabel("Date de naissance:"), 1, 0)
            info_layout.addWidget(QLabel(eleve.date_naissance.strftime("%d/%m/%Y") if eleve.date_naissance else ""), 1, 1)
            
            info_layout.addWidget(QLabel("Contact parent:"), 2, 0)
            info_layout.addWidget(QLabel(getattr(eleve, 'contact_parent', '') or "Non renseigné"), 2, 1)
            
            info_group.setLayout(info_layout)
            layout.addWidget(info_group)
            
            # Récupérer l'historique des classes
            historique_query = session.execute(
                text("""
                    SELECT c.id as classe_id, c.nom as classe_nom, h.date_debut, h.date_fin
                    FROM eleve_classe_historique h
                    JOIN classes c ON h.classe_id = c.id
                    WHERE h.eleve_id = :eleve_id
                    ORDER BY h.date_debut DESC
                """),
                {"eleve_id": eleve_id}
            )
            
            historiques = historique_query.fetchall()
            
            # Créer un onglet pour chaque classe dans l'historique
            tab_widget = QTabWidget()
            
            for idx, (classe_id, classe_nom, date_debut, date_fin) in enumerate(historiques):
                # Créer un onglet pour cette classe
                classe_tab = QWidget()
                classe_layout = QVBoxLayout(classe_tab)
                
                # Informations sur la période dans cette classe
                period_info = QGroupBox(f"Période dans la classe: {classe_nom}")
                period_layout = QGridLayout()
                
                # Date début
                if date_debut:
                    if isinstance(date_debut, str):
                        try:
                            date_debut = datetime.strptime(date_debut, "%Y-%m-%d %H:%M:%S")
                        except:
                            date_debut = None
                
                date_debut_str = date_debut.strftime("%d/%m/%Y") if date_debut else "Inconnue"
                period_layout.addWidget(QLabel("Date début:"), 0, 0)
                period_layout.addWidget(QLabel(date_debut_str), 0, 1)
                
                # Date fin
                date_fin_str = "En cours"
                if date_fin:
                    if isinstance(date_fin, str):
                        try:
                            date_fin = datetime.strptime(date_fin, "%Y-%m-%d %H:%M:%S")
                            date_fin_str = date_fin.strftime("%d/%m/%Y")
                        except:
                            pass
                
                period_layout.addWidget(QLabel("Date fin:"), 1, 0)
                period_layout.addWidget(QLabel(date_fin_str), 1, 1)
                
                # Durée
                if date_debut:
                    end_date = date_fin if date_fin else datetime.now()
                    if isinstance(end_date, datetime):
                        duree = (end_date - date_debut).days
                        period_layout.addWidget(QLabel("Durée:"), 2, 0)
                        period_layout.addWidget(QLabel(f"{duree} jours"), 2, 1)
                
                period_info.setLayout(period_layout)
                classe_layout.addWidget(period_info)
                
                # Récupérer les notes pour cette classe
                notes = self.get_notes_by_classe(session, eleve_id, classe_id)
                
                if notes:
                    # Tableau des notes
                    notes_label = QLabel(f"Notes obtenues en {classe_nom}:")
                    notes_label.setStyleSheet("font-weight: bold; font-size: 13px; margin-top: 10px;")
                    classe_layout.addWidget(notes_label)
                    
                    notes_table = QTableWidget()
                    notes_table.setColumnCount(4)
                    notes_table.setHorizontalHeaderLabels(["Matière", "Note", "Coefficient", "Date"])
                    
                    # Configurer le tableau des notes
                    notes_table.setRowCount(len(notes))
                    notes_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
                    notes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
                    notes_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
                    notes_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
                    notes_table.setColumnWidth(1, 70)
                    notes_table.setColumnWidth(2, 100)
                    notes_table.setColumnWidth(3, 120)
                    notes_table.verticalHeader().setVisible(False)
                    notes_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                    
                    # Remplir le tableau des notes
                    total_points = 0
                    total_coefficients = 0
                    
                    for row_idx, (matiere, note, coefficient, date_note) in enumerate(notes):
                        # Matière
                        notes_table.setItem(row_idx, 0, QTableWidgetItem(matiere))
                        
                        # Note
                        note_item = QTableWidgetItem(str(note))
                        note_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        # Colorer selon la note
                        try:
                            note_float = float(note)
                            if note_float >= 16:
                                note_item.setForeground(QColor("#4CAF50"))  # Vert
                            elif note_float >= 10:
                                note_item.setForeground(QColor("#FF9800"))  # Orange
                            else:
                                note_item.setForeground(QColor("#F44336"))  # Rouge
                        except:
                            pass
                        notes_table.setItem(row_idx, 1, note_item)
                        
                        # Coefficient
                        coeff_item = QTableWidgetItem(str(coefficient) if coefficient else "1")
                        coeff_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        notes_table.setItem(row_idx, 2, coeff_item)
                        
                        # Date
                        date_str = ""
                        if date_note:
                            if isinstance(date_note, str):
                                try:
                                    date_note = datetime.strptime(date_note, "%Y-%m-%d %H:%M:%S")
                                    date_str = date_note.strftime("%d/%m/%Y")
                                except:
                                    date_str = date_note
                            else:
                                date_str = date_note.strftime("%d/%m/%Y")
                        date_item = QTableWidgetItem(date_str)
                        date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        notes_table.setItem(row_idx, 3, date_item)
                        
                        # Calcul pour la moyenne
                        try:
                            total_points += float(note) * (float(coefficient) if coefficient else 1)
                            total_coefficients += float(coefficient) if coefficient else 1
                        except:
                            pass
                    
                    classe_layout.addWidget(notes_table)
                    
                    # Calcul et affichage de la moyenne
                    if total_coefficients > 0:
                        moyenne = total_points / total_coefficients
                        moyenne_label = QLabel(f"Moyenne générale: {moyenne:.2f}/20")
                        moyenne_label.setStyleSheet("""
                            QLabel {
                                font-weight: bold;
                                font-size: 14px;
                                padding: 8px;
                                background-color: #e8f5e9;
                                border-radius: 6px;
                                border: 1px solid #4CAF50;
                                margin-top: 10px;
                            }
                        """)
                        classe_layout.addWidget(moyenne_label)
                else:
                    # Pas de notes pour cette classe
                    no_notes_label = QLabel(f"Aucune note enregistrée pour la classe {classe_nom}")
                    no_notes_label.setStyleSheet("""
                        QLabel {
                            color: #666;
                            font-style: italic;
                            padding: 20px;
                            background-color: #f5f5f5;
                            border-radius: 6px;
                            border: 1px dashed #ccc;
                            margin-top: 10px;
                        }
                    """)
                    no_notes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    classe_layout.addWidget(no_notes_label)
                
                classe_layout.addStretch()
                
                # Ajouter l'onglet au widget d'onglets
                tab_widget.addTab(classe_tab, classe_nom)
            
            layout.addWidget(tab_widget)
            
            # Bouton Fermer
            btn_close = QPushButton("Fermer")
            btn_close.setFixedHeight(40)
            btn_close.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0px 20px;
                    font-weight: bold;
                    font-size: 14px;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #545b62;
                }
            """)
            btn_close.clicked.connect(dialog.accept)
            layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)
            
        except Exception as e:
            QMessageBox.critical(dialog, "Erreur", f"Erreur lors du chargement de l'historique: {str(e)}")
        finally:
            session.close()
        
        dialog.exec()

    def filter_eleves(self):
        """Filtre les élèves selon les critères (recherche, classe, sexe)"""
        search_text = self.search_input.text().lower()
        classe_id = self.classe_filter.currentData()
        sexe = self.sexe_filter.currentData()
        
        rows_visible = 0
        
        for row in range(self.table_eleves.rowCount()):
            item = self.table_eleves.item(row, 0)
            if item and item.text() == "Aucun élève enregistré":
                continue
                
            nom_item = self.table_eleves.item(row, 1)
            prenom_item = self.table_eleves.item(row, 2)
            classe_item = self.table_eleves.item(row, 3)
            sexe_item = self.table_eleves.item(row, 4)
            
            if nom_item and prenom_item:
                nom = nom_item.text().lower()
                prenom = prenom_item.text().lower()
                
                # Filtre de recherche
                search_match = search_text in nom or search_text in prenom
                
                # Filtre de classe
                if classe_id:
                    classe_match = classe_item and classe_item.text() == self.classe_filter.currentText()
                else:
                    classe_match = True
                
                # Filtre de sexe
                if sexe:
                    if sexe_item:
                        sexe_text = sexe_item.text()
                        if sexe == SexeEnum.MASCULIN and "M" in sexe_text:
                            sexe_match = True
                        elif sexe == SexeEnum.FEMININ and "F" in sexe_text:
                            sexe_match = True
                        else:
                            sexe_match = False
                    else:
                        sexe_match = False
                else:
                    sexe_match = True
                
                visible = search_match and classe_match and sexe_match
                self.table_eleves.setRowHidden(row, not visible)
                
                if visible:
                    rows_visible += 1
        
        if rows_visible > 0:
            self.stats_label.setText(f"Affichage de {rows_visible} élève(s)")

    def update_stats(self):
        """Met à jour les statistiques"""
        session = SessionLocal()
        try:
            # Compter tous les élèves
            total_eleves = session.query(Eleve).count()
            
            if total_eleves == 0:
                self.stats_label.setText(" Aucun élève enregistré")
                return
            
            # Compter par classe - CORRECTION ICI
            classes_stats = []
            classes = session.query(Classe).all()
            for classe in classes:
                count = session.query(Eleve).filter(Eleve.classe_actuelle_id == classe.id).count()
                if count > 0:
                    classes_stats.append(f"{classe.nom}: {count}")
            
            # Compter par sexe
            masculin = session.query(Eleve).filter(Eleve.sexe == SexeEnum.MASCULIN).count()
            feminin = session.query(Eleve).filter(Eleve.sexe == SexeEnum.FEMININ).count()
            
            # Compter les élèves avec contact parent
            eleves_avec_contact = session.query(Eleve).filter(
                Eleve.contact_parent.isnot(None)
            ).count() if hasattr(Eleve, 'contact_parent') else 0
            
            stats_text = f"Total: {total_eleves} élève(s)"
            
            if classes_stats:
                stats_text += " | Par classe: "
                stats_text += " | ".join(classes_stats)  # CORRECTION: Utiliser directement les chaînes
            
            stats_text += f" | Masculin: {masculin} | Féminin: {feminin}"
            
            if hasattr(Eleve, 'contact_parent'):
                stats_text += f" | Avec contact: {eleves_avec_contact}"
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            print(f"Erreur dans update_stats: {e}")
            self.stats_label.setText("Erreur de chargement des statistiques")
        finally:
            session.close()

    def show_add_dialog(self):
        """Affiche le dialogue d'ajout"""
        dialog = EleveFormDialog(self)
        if dialog.exec():
            print("Élève ajouté, rechargement des données...")
            self.load_eleves()

    def show_edit_dialog(self, eleve_id):
        """Affiche le dialogue de modification"""
        dialog = EleveFormDialog(self, eleve_id)
        if dialog.exec():
            print("Élève modifié, rechargement des données...")
            self.load_eleves()

    def delete_eleve(self, eleve_id):
        """Supprime un élève"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cet élève ?\n\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = SessionLocal()
            try:
                eleve = session.query(Eleve).filter(Eleve.id == eleve_id).first()
                if eleve:
                    # Supprimer d'abord l'historique des classes
                    session.execute(
                        text("DELETE FROM eleve_classe_historique WHERE eleve_id = :eleve_id"),
                        {"eleve_id": eleve_id}
                    )
                    # Puis supprimer l'élève
                    session.delete(eleve)
                    session.commit()
                    QMessageBox.information(self, "Succès", "Élève supprimé avec succès!")
                    print("Élève supprimé, rechargement des données...")
                    self.load_eleves()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
            finally:
                session.close()