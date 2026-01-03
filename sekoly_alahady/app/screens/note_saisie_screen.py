from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QMessageBox,
    QAbstractItemView, QLineEdit, QDateEdit, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from app.databases.db import SessionLocal
from app.databases.models import Eleve, Classe, Note, TypeExamen
from datetime import datetime


class DateExamenDialog(QDialog):
    """Dialogue pour sélectionner la date de l'examen"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Date de l'examen")
        self.setFixedSize(300, 150)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.date_examen = QDateEdit()
        self.date_examen.setDate(QDate.currentDate())
        self.date_examen.setCalendarPopup(True)
        self.date_examen.setStyleSheet("""
            QDateEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #333333;
                height: 40px;
            }
            QDateEdit:focus {
                border-color: #4070f4;
                background-color: #f8fbff;
            }
        """)
        
        form_layout.addRow("Date de l'examen:", self.date_examen)
        layout.addLayout(form_layout)

        # Boutons
        button_layout = QHBoxLayout()
        
        btn_ok = QPushButton("Valider")
        btn_ok.setFixedHeight(40)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        btn_ok.clicked.connect(self.accept)
        
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
        button_layout.addWidget(btn_ok)

        layout.addLayout(button_layout)

    def get_date(self):
        """Retourne la date sélectionnée"""
        return self.date_examen.date().toPyDate()


class NoteSaisieScreen(QWidget):
    """Page de saisie des notes"""
    def __init__(self):
        super().__init__()
        self.selected_classe_id = None
        self.type_examens = []  # Liste des types d'examen (max 6)
        self.date_examen = None  # Date de l'examen (commune pour toutes les notes)
        self.init_ui()
        self.load_classes()
        self.load_type_examens()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # En-tête
        header_layout = QHBoxLayout()
        
        title = QLabel("Saisie des Notes")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e1f29; margin-bottom: 5px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Contrôles de configuration
        config_frame = QFrame()
        config_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        config_layout = QHBoxLayout(config_frame)
        config_layout.setContentsMargins(10, 10, 10, 10)
        
        # Sélection de la classe
        self.classe_combo = QComboBox()
        self.classe_combo.setFixedHeight(40)
        self.classe_combo.setPlaceholderText("Sélectionnez une classe")
        self.classe_combo.currentIndexChanged.connect(self.on_classe_changed)
        
        # Bouton pour sélectionner la date de l'examen
        self.btn_date = QPushButton("Sélectionner la date")
        self.btn_date.setFixedHeight(40)
        self.btn_date.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #999999;
            }
        """)
        self.btn_date.clicked.connect(self.select_date_examen)
        self.btn_date.setEnabled(False)  # Désactivé jusqu'à ce qu'une classe soit sélectionnée
        
        # Label pour afficher la date sélectionnée
        self.label_date = QLabel("Date non définie")
        self.label_date.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                font-style: italic;
                padding: 5px 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        combo_style = """
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #333333;
                min-width: 250px;
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
        
        self.classe_combo.setStyleSheet(combo_style)

        config_layout.addWidget(QLabel("Classe:"))
        config_layout.addWidget(self.classe_combo, 1)
        config_layout.addWidget(QLabel("Date examen:"))
        config_layout.addWidget(self.label_date)
        config_layout.addWidget(self.btn_date)
        
        main_layout.addWidget(config_frame)

        # Tableau des notes
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
        
        self.table_notes = QTableWidget()
        table_container_layout.addWidget(self.table_notes)
        
        main_layout.addWidget(table_container, 1)

        # Bouton de sauvegarde
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_save = QPushButton("Sauvegarder les notes")
        self.btn_save.setFixedHeight(45)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0px 25px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.btn_save.clicked.connect(self.save_notes)
        self.btn_save.setEnabled(False)  # Désactivé jusqu'à ce qu'une classe et une date soient sélectionnées
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_save)
        
        main_layout.addWidget(button_frame)

    def load_classes(self):
        """Charge les classes dans le filtre"""
        session = SessionLocal()
        try:
            classes = session.query(Classe).order_by(Classe.ordre).all()
            self.classe_combo.clear()
            self.classe_combo.addItem("-- Sélectionnez une classe --", None)
            for classe in classes:
                self.classe_combo.addItem(classe.nom, classe.id)
        finally:
            session.close()

    def load_type_examens(self):
        """Charge les types d'examen (maximum 6)"""
        session = SessionLocal()
        try:
            self.type_examens = session.query(TypeExamen).limit(6).all()
        finally:
            session.close()

    def on_classe_changed(self):
        """Gère le changement de classe"""
        classe_id = self.classe_combo.currentData()
        
        if not classe_id:
            self.table_notes.clear()
            self.table_notes.setRowCount(0)
            self.table_notes.setColumnCount(0)
            self.btn_save.setEnabled(False)
            self.btn_date.setEnabled(False)
            self.date_examen = None
            self.label_date.setText("Date non définie")
            return
        
        self.selected_classe_id = classe_id
        self.btn_date.setEnabled(True)
        
        # Si une date est déjà définie, recharger les notes
        if self.date_examen:
            self.load_eleves_notes()

    def select_date_examen(self):
        """Ouvre le dialogue pour sélectionner la date de l'examen"""
        dialog = DateExamenDialog(self)
        if dialog.exec():
            self.date_examen = dialog.get_date()
            self.label_date.setText(self.date_examen.strftime("%d/%m/%Y"))
            
            # Mettre à jour l'état du bouton de sauvegarde
            if self.selected_classe_id and self.date_examen:
                self.btn_save.setEnabled(True)
                self.load_eleves_notes()
            else:
                self.btn_save.setEnabled(False)

    def load_eleves_notes(self):
        """Charge les élèves et leurs notes pour la classe et date sélectionnées"""
        if not self.selected_classe_id or not self.date_examen:
            return
        
        session = SessionLocal()
        try:
            # Charger les élèves de la classe
            eleves = session.query(Eleve).filter(
                Eleve.classe_actuelle_id == self.selected_classe_id
            ).order_by(Eleve.nom, Eleve.prenom).all()
            
            # Configurer le tableau
            num_columns = 3 + len(self.type_examens)  # ID + Nom + Prénom + colonnes notes
            self.table_notes.setColumnCount(num_columns)
            
            # En-têtes des colonnes
            headers = ["ID", "Nom", "Prénom"]
            headers.extend([exam.abreviation for exam in self.type_examens])
            self.table_notes.setHorizontalHeaderLabels(headers)
            
            # Configurer les largeurs de colonnes
            header = self.table_notes.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nom
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Prénom
            
            self.table_notes.setColumnWidth(0, 50)
            
            # Largeur fixe pour les colonnes de notes
            for i in range(3, num_columns):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                self.table_notes.setColumnWidth(i, 80)
            
            self.table_notes.verticalHeader().setDefaultSectionSize(40)
            self.table_notes.verticalHeader().setVisible(False)
            
            # Style du tableau
            self.table_notes.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: none;
                    border-radius: 12px;
                    gridline-color: #f0f0f0;
                    alternate-background-color: #f9f9f9;
                    font-size: 13px;
                }
                QTableWidget::item {
                    padding: 8px;
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
                    font-size: 12px;
                    color: #1e1f29;
                    text-align: center;
                }
            """)
            
            self.table_notes.setAlternatingRowColors(True)
            self.table_notes.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
            
            # Remplir le tableau avec les élèves
            self.table_notes.setRowCount(len(eleves))
            
            for row, eleve in enumerate(eleves):
                # ID (lecture seule)
                item_id = QTableWidgetItem(str(eleve.id))
                item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_notes.setItem(row, 0, item_id)
                
                # Nom
                item_nom = QTableWidgetItem(eleve.nom.upper() if eleve.nom else "")
                item_nom.setFlags(item_nom.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item_nom.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                self.table_notes.setItem(row, 1, item_nom)
                
                # Prénom
                item_prenom = QTableWidgetItem(eleve.prenom or "")
                item_prenom.setFlags(item_prenom.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_notes.setItem(row, 2, item_prenom)
                
                # Charger les notes existantes pour chaque type d'examen, la classe et la date
                for col, type_examen in enumerate(self.type_examens, start=3):
                    # Chercher si une note existe pour cet élève, ce type d'examen, cette classe et cette date
                    note = session.query(Note).filter(
                        Note.eleve_id == eleve.id,
                        Note.type_examen_id == type_examen.id,
                        Note.classe_id == self.selected_classe_id,
                        Note.date_examen == self.date_examen
                    ).first()
                    
                    # Créer un widget d'édition pour la note
                    note_item = QTableWidgetItem()
                    if note and note.note is not None:
                        note_item.setText(str(note.note))
                    
                    # Autoriser l'édition uniquement pour les colonnes de notes
                    note_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table_notes.setItem(row, col, note_item)
            
        except Exception as e:
            print(f"Erreur lors du chargement des élèves/notes: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")
        finally:
            session.close()

    def save_notes(self):
        """Sauvegarde toutes les notes modifiées"""
        if not self.selected_classe_id or not self.date_examen:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une classe et une date")
            return
        
        session = SessionLocal()
        try:
            modifications = 0
            errors = []
            
            # Vérifier si l'examen n'est pas dans le futur
            if self.date_examen > datetime.now().date():
                reply = QMessageBox.question(
                    self,
                    "Confirmation",
                    f"La date de l'examen ({self.date_examen.strftime('%d/%m/%Y')}) est dans le futur.\nVoulez-vous continuer ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            for row in range(self.table_notes.rowCount()):
                eleve_id_item = self.table_notes.item(row, 0)
                if not eleve_id_item:
                    continue
                
                eleve_id = int(eleve_id_item.text())
                
                for col, type_examen in enumerate(self.type_examens, start=3):
                    note_item = self.table_notes.item(row, col)
                    note_text = note_item.text().strip() if note_item else ""
                    
                    # Chercher la note existante
                    note = session.query(Note).filter(
                        Note.eleve_id == eleve_id,
                        Note.type_examen_id == type_examen.id,
                        Note.classe_id == self.selected_classe_id,
                        Note.date_examen == self.date_examen
                    ).first()
                    
                    # Si le champ est vide et qu'une note existe, la supprimer
                    if not note_text:
                        if note:
                            session.delete(note)
                            modifications += 1
                        continue
                    
                    # Valider que c'est un nombre
                    try:
                        note_value = float(note_text)
                        if note_value < 0 or note_value > 20:
                            errors.append(f"Ligne {row+1}, {type_examen.abreviation}: Note {note_value} hors limites (0-20)")
                            continue
                    except ValueError:
                        errors.append(f"Ligne {row+1}, {type_examen.abreviation}: '{note_text}' n'est pas un nombre valide")
                        continue
                    
                    # Mettre à jour ou créer la note
                    if note:
                        note.note = note_value
                    else:
                        # IMPORTANT: Vérifier si l'élève était dans cette classe à la date de l'examen
                        # en consultant l'historique des classes
                        historique_query = session.execute(
                            f"""
                            SELECT 1 FROM eleve_classe_historique
                            WHERE eleve_id = :eleve_id
                            AND classe_id = :classe_id
                            AND date_debut <= :date_examen
                            AND (date_fin IS NULL OR date_fin >= :date_examen)
                            """,
                            {
                                "eleve_id": eleve_id,
                                "classe_id": self.selected_classe_id,
                                "date_examen": self.date_examen
                            }
                        )
                        
                        if not historique_query.fetchone():
                            errors.append(
                                f"Ligne {row+1}: L'élève n'était pas dans cette classe à la date {self.date_examen.strftime('%d/%m/%Y')}"
                            )
                            continue
                        
                        new_note = Note(
                            eleve_id=eleve_id,
                            type_examen_id=type_examen.id,
                            classe_id=self.selected_classe_id,
                            date_examen=self.date_examen,
                            note=note_value
                        )
                        session.add(new_note)
                    modifications += 1
            
            if errors:
                error_msg = "Des erreurs ont été détectées:\n\n" + "\n".join(errors[:10])  # Afficher seulement les 10 premières erreurs
                if len(errors) > 10:
                    error_msg += f"\n\n... et {len(errors) - 10} autres erreurs."
                QMessageBox.warning(self, "Erreurs de validation", error_msg)
                session.rollback()
                return
            
            session.commit()
            
            if modifications > 0:
                QMessageBox.information(self, "Succès", f"{modifications} notes sauvegardées avec succès!")
            else:
                QMessageBox.information(self, "Information", "Aucune modification à sauvegarder.")
            
            self.load_eleves_notes()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
        finally:
            session.close()