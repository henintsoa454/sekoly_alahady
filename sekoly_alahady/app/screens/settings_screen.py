from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox,
    QMessageBox, QDialog, QFormLayout, QAbstractItemView, QTabWidget
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from app.databases.db import SessionLocal
from app.databases.models import ModelAttribute
from app.databases.dynamic_schema import DynamicSchemaManager
from sqlalchemy import inspect


class AttributeFormDialog(QDialog):
    """Dialogue pour ajouter/modifier un attribut"""
    def __init__(self, parent=None, attribute_id=None, model_name=None):
        super().__init__(parent)
        self.attribute_id = attribute_id
        self.model_name = model_name
        self.setWindowTitle("Modifier l'attribut" if attribute_id else "Ajouter un attribut")
        self.setFixedSize(500, 400)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Sélection du modèle (si pas déjà défini)
        if not self.model_name:
            self.model_combo = QComboBox()
            self.model_combo.addItem("Eleve", "Eleve")
            self.model_combo.addItem("Professeur", "Professeur")
            self.model_combo.addItem("Classe", "Classe")
            self.model_combo.addItem("Note", "Note")
            self.model_combo.addItem("TypeExamen", "TypeExamen")
            form_layout.addRow("Modèle:", self.model_combo)
        else:
            self.model_combo = None
        
        # Nom de l'attribut
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("nom_attribut")
        form_layout.addRow("Nom de l'attribut:", self.name_input)
        
        # Type de l'attribut
        self.type_combo = QComboBox()
        self.type_combo.addItem("String", "String")
        self.type_combo.addItem("Integer", "Integer")
        self.type_combo.addItem("Float", "Float")
        self.type_combo.addItem("Date", "Date")
        self.type_combo.addItem("DateTime", "DateTime")
        self.type_combo.addItem("Boolean", "Boolean")
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form_layout.addRow("Type:", self.type_combo)
        
        # Longueur maximale (pour String)
        self.max_length_input = QLineEdit()
        self.max_length_input.setPlaceholderText("Ex: 100")
        self.max_length_input.setEnabled(False)
        form_layout.addRow("Longueur max (String):", self.max_length_input)
        
        # Valeur par défaut
        self.default_input = QLineEdit()
        self.default_input.setPlaceholderText("Valeur par défaut (optionnel)")
        self.default_input.textChanged.connect(self.on_default_value_changed)
        form_layout.addRow("Valeur par défaut:", self.default_input)
        
        # Label d'aide pour la valeur par défaut
        self.default_help_label = QLabel("")
        self.default_help_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        self.default_help_label.setWordWrap(True)
        form_layout.addRow("", self.default_help_label)
        
        # Nullable
        self.nullable_combo = QComboBox()
        self.nullable_combo.addItem("Oui", True)
        self.nullable_combo.addItem("Non", False)
        self.nullable_combo.currentIndexChanged.connect(self.on_nullable_changed)
        form_layout.addRow("Peut être NULL:", self.nullable_combo)
        
        # Nom d'affichage
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("Nom d'affichage dans l'interface")
        form_layout.addRow("Nom d'affichage:", self.display_name_input)
        
        # Style
        for widget in [self.name_input, self.type_combo, self.max_length_input, 
                      self.default_input, self.nullable_combo, self.display_name_input]:
            if widget:
                widget.setFixedHeight(40)
                widget.setStyleSheet("""
                    QLineEdit, QComboBox {
                        border: 2px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 14px;
                    }
                    QLineEdit:focus, QComboBox:focus {
                        border-color: #4070f4;
                    }
                """)
        
        if self.model_combo:
            self.model_combo.setFixedHeight(40)
            self.model_combo.setStyleSheet("""
                QComboBox {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                }
                QComboBox:focus {
                    border-color: #4070f4;
                }
            """)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
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
        """)
        btn_save.clicked.connect(self.save_attribute)
        
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
        """)
        btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(btn_cancel)
        button_layout.addStretch()
        button_layout.addWidget(btn_save)
        
        layout.addLayout(button_layout)
    
    def on_type_changed(self):
        """Active/désactive le champ longueur max selon le type"""
        current_type = self.type_combo.currentData()
        self.max_length_input.setEnabled(current_type == "String")
        
        # Mettre à jour le placeholder et l'aide de la valeur par défaut
        placeholders = {
            "String": "Ex: 'Valeur par défaut'",
            "Integer": "Ex: 0, 10, -5",
            "Float": "Ex: 0.0, 10.5, -3.14",
            "Date": "Ex: 2024-01-01 (format YYYY-MM-DD)",
            "DateTime": "Ex: 2024-01-01 12:00:00",
            "Boolean": "Ex: true, false, 1, 0"
        }
        
        help_texts = {
            "String": "Texte libre. Si longueur max est définie, la valeur ne doit pas la dépasser.",
            "Integer": "Nombre entier (ex: 0, 10, -5)",
            "Float": "Nombre décimal (ex: 0.0, 10.5, -3.14)",
            "Date": "Format: YYYY-MM-DD (ex: 2024-01-01) ou DD/MM/YYYY (ex: 01/01/2024)",
            "DateTime": "Format: YYYY-MM-DD HH:MM:SS (ex: 2024-01-01 12:00:00)",
            "Boolean": "Valeurs acceptées: true, false, 1, 0, yes, no, oui, non"
        }
        
        placeholder = placeholders.get(current_type, "Valeur par défaut")
        help_text = help_texts.get(current_type, "")
        
        self.default_input.setPlaceholderText(placeholder)
        self.default_help_label.setText(help_text)
        
        # Vérifier si une valeur par défaut est nécessaire (si nullable = Non)
        is_nullable = self.nullable_combo.currentData()
        if not is_nullable and not self.default_input.text().strip():
            self.default_help_label.setText(f"⚠ OBLIGATOIRE: {help_text}")
            self.default_help_label.setStyleSheet("color: #ff9800; font-size: 11px; font-weight: bold;")
        else:
            # Valider la valeur actuelle si elle existe
            if self.default_input.text().strip():
                self.on_default_value_changed()
            else:
                self.default_help_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
    
    def on_nullable_changed(self):
        """Gère le changement de l'option nullable"""
        is_nullable = self.nullable_combo.currentData()
        default_value = self.default_input.text().strip()
        
        # Si l'attribut n'est pas nullable et qu'il n'y a pas de valeur par défaut
        if not is_nullable and not default_value:
            self.default_help_label.setText("⚠ Une valeur par défaut est obligatoire si l'attribut n'est pas nullable")
            self.default_help_label.setStyleSheet("color: #dc3545; font-size: 11px;")
        else:
            # Valider la valeur actuelle si elle existe
            if default_value:
                self.on_default_value_changed()
            else:
                # Récupérer le texte d'aide selon le type
                attribute_type = self.type_combo.currentData()
                help_texts = {
                    "String": "Texte libre. Si longueur max est définie, la valeur ne doit pas la dépasser.",
                    "Integer": "Nombre entier (ex: 0, 10, -5)",
                    "Float": "Nombre décimal (ex: 0.0, 10.5, -3.14)",
                    "Date": "Format: YYYY-MM-DD (ex: 2024-01-01) ou DD/MM/YYYY (ex: 01/01/2024)",
                    "DateTime": "Format: YYYY-MM-DD HH:MM:SS (ex: 2024-01-01 12:00:00)",
                    "Boolean": "Valeurs acceptées: true, false, 1, 0, yes, no, oui, non"
                }
                help_text = help_texts.get(attribute_type, "")
                if not is_nullable:
                    help_text = f"⚠ OBLIGATOIRE: {help_text}"
                    self.default_help_label.setStyleSheet("color: #ff9800; font-size: 11px; font-weight: bold;")
                else:
                    self.default_help_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
                self.default_help_label.setText(help_text)
    
    def on_default_value_changed(self):
        """Valide la valeur par défaut en temps réel"""
        value = self.default_input.text().strip()
        attribute_type = self.type_combo.currentData()
        is_nullable = self.nullable_combo.currentData()
        
        if not value:
            # Si pas de valeur et que l'attribut n'est pas nullable, afficher un avertissement
            if not is_nullable:
                self.default_help_label.setText("⚠ Une valeur par défaut est obligatoire si l'attribut n'est pas nullable")
                self.default_help_label.setStyleSheet("color: #dc3545; font-size: 11px;")
            else:
                # Récupérer le texte d'aide selon le type
                help_texts = {
                    "String": "Texte libre. Si longueur max est définie, la valeur ne doit pas la dépasser.",
                    "Integer": "Nombre entier (ex: 0, 10, -5)",
                    "Float": "Nombre décimal (ex: 0.0, 10.5, -3.14)",
                    "Date": "Format: YYYY-MM-DD (ex: 2024-01-01) ou DD/MM/YYYY (ex: 01/01/2024)",
                    "DateTime": "Format: YYYY-MM-DD HH:MM:SS (ex: 2024-01-01 12:00:00)",
                    "Boolean": "Valeurs acceptées: true, false, 1, 0, yes, no, oui, non"
                }
                help_text = help_texts.get(attribute_type, "")
                self.default_help_label.setText(help_text)
                self.default_help_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
            return
        
        error = self._validate_default_value(value, attribute_type)
        if error:
            self.default_help_label.setText(f"⚠ {error}")
            self.default_help_label.setStyleSheet("color: #dc3545; font-size: 11px;")
        else:
            # Récupérer le texte d'aide original
            help_texts = {
                "String": "Texte libre. Si longueur max est définie, la valeur ne doit pas la dépasser.",
                "Integer": "Nombre entier (ex: 0, 10, -5)",
                "Float": "Nombre décimal (ex: 0.0, 10.5, -3.14)",
                "Date": "Format: YYYY-MM-DD (ex: 2024-01-01) ou DD/MM/YYYY (ex: 01/01/2024)",
                "DateTime": "Format: YYYY-MM-DD HH:MM:SS (ex: 2024-01-01 12:00:00)",
                "Boolean": "Valeurs acceptées: true, false, 1, 0, yes, no, oui, non"
            }
            help_text = help_texts.get(attribute_type, "")
            self.default_help_label.setText(f"✓ {help_text}")
            self.default_help_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
    
    def _validate_default_value(self, value, attribute_type):
        """Valide qu'une valeur par défaut est compatible avec le type"""
        if not value:
            return None  # Pas de valeur = pas d'erreur
        
        value = value.strip()
        
        if attribute_type == "String":
            # Les strings sont toujours valides (peuvent être vides)
            # Vérifier la longueur max si définie
            if self.max_length_input.isEnabled() and self.max_length_input.text().strip():
                try:
                    max_len = int(self.max_length_input.text().strip())
                    if len(value) > max_len:
                        return f"La valeur par défaut dépasse la longueur maximale ({max_len} caractères)"
                except:
                    pass
            return None  # Valide
        
        elif attribute_type == "Integer":
            try:
                int(value)
                return None  # Valide
            except ValueError:
                return f"La valeur '{value}' n'est pas un entier valide. Exemples: 0, 10, -5"
        
        elif attribute_type == "Float":
            try:
                float(value)
                return None  # Valide
            except ValueError:
                return f"La valeur '{value}' n'est pas un nombre décimal valide. Exemples: 0.0, 10.5, -3.14"
        
        elif attribute_type == "Date":
            from datetime import datetime
            try:
                # Essayer différents formats de date
                formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
                parsed = False
                for fmt in formats:
                    try:
                        datetime.strptime(value, fmt)
                        parsed = True
                        break
                    except ValueError:
                        continue
                if not parsed:
                    return f"La valeur '{value}' n'est pas une date valide. Format attendu: YYYY-MM-DD (ex: 2024-01-01)"
                return None  # Valide
            except Exception as e:
                return f"Erreur de format de date: {str(e)}"
        
        elif attribute_type == "DateTime":
            from datetime import datetime
            try:
                # Essayer différents formats de datetime
                formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S"]
                parsed = False
                for fmt in formats:
                    try:
                        datetime.strptime(value, fmt)
                        parsed = True
                        break
                    except ValueError:
                        continue
                if not parsed:
                    return f"La valeur '{value}' n'est pas une date/heure valide. Format attendu: YYYY-MM-DD HH:MM:SS"
                return None  # Valide
            except Exception as e:
                return f"Erreur de format de date/heure: {str(e)}"
        
        elif attribute_type == "Boolean":
            # Accepter plusieurs formats pour les booléens
            value_lower = value.lower()
            valid_values = ["true", "false", "1", "0", "yes", "no", "oui", "non"]
            if value_lower in valid_values:
                return None  # Valide
            else:
                return f"La valeur '{value}' n'est pas un booléen valide. Valeurs acceptées: true, false, 1, 0, yes, no"
        
        return None  # Type inconnu, on accepte
    
    def load_data(self):
        """Charge les données si modification"""
        if self.attribute_id:
            session = SessionLocal()
            try:
                attr = session.query(ModelAttribute).filter(
                    ModelAttribute.id == self.attribute_id
                ).first()
                if attr:
                    if self.model_combo:
                        index = self.model_combo.findData(attr.model_name)
                        if index >= 0:
                            self.model_combo.setCurrentIndex(index)
                    self.name_input.setText(attr.attribute_name)
                    index = self.type_combo.findData(attr.attribute_type)
                    if index >= 0:
                        self.type_combo.setCurrentIndex(index)
                    if attr.max_length:
                        self.max_length_input.setText(str(attr.max_length))
                    if attr.default_value:
                        self.default_input.setText(attr.default_value)
                    index = self.nullable_combo.findData(attr.is_nullable)
                    if index >= 0:
                        self.nullable_combo.setCurrentIndex(index)
                    if attr.display_name:
                        self.display_name_input.setText(attr.display_name)
            finally:
                session.close()
    
    def save_attribute(self):
        """Sauvegarde l'attribut"""
        model_name = self.model_combo.currentData() if self.model_combo else self.model_name
        attribute_name = self.name_input.text().strip()
        attribute_type = self.type_combo.currentData()
        max_length = None
        if self.max_length_input.isEnabled() and self.max_length_input.text().strip():
            try:
                max_length = int(self.max_length_input.text().strip())
            except:
                QMessageBox.warning(self, "Erreur", "La longueur maximale doit être un nombre")
                return
        
        default_value = self.default_input.text().strip() or None
        is_nullable = self.nullable_combo.currentData()
        display_name = self.display_name_input.text().strip() or None
        
        # Validation
        if not attribute_name:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir un nom d'attribut")
            return
        
        # Vérifier que le nom n'est pas réservé
        reserved_names = ["id", "created_at", "updated_at"]
        if attribute_name.lower() in reserved_names:
            QMessageBox.warning(self, "Erreur", f"Le nom '{attribute_name}' est réservé")
            return
        
        # Validation : si l'attribut n'est pas nullable, une valeur par défaut est obligatoire
        if not is_nullable and not default_value:
            QMessageBox.warning(
                self, 
                "Erreur de validation", 
                "Un attribut qui ne peut pas être NULL doit avoir une valeur par défaut.\n\n"
                "Veuillez soit :\n"
                "- Ajouter une valeur par défaut, ou\n"
                "- Autoriser les valeurs NULL (Nullable = Oui)"
            )
            return
        
        # Validation de la valeur par défaut selon le type
        if default_value:
            validation_error = self._validate_default_value(default_value, attribute_type)
            if validation_error:
                QMessageBox.warning(self, "Erreur de validation", validation_error)
                return
        
        session = SessionLocal()
        try:
            if self.attribute_id:
                # Modification (seulement des métadonnées, pas de la colonne)
                attr = session.query(ModelAttribute).filter(
                    ModelAttribute.id == self.attribute_id
                ).first()
                if attr:
                    attr.attribute_name = attribute_name
                    attr.attribute_type = attribute_type
                    attr.max_length = max_length
                    attr.default_value = default_value
                    attr.is_nullable = is_nullable
                    attr.display_name = display_name
                    message = "Attribut modifié avec succès!"
            else:
                # Ajout - créer la colonne dans la base de données
                try:
                    DynamicSchemaManager.add_column(
                        model_name, attribute_name, attribute_type,
                        default_value, max_length, is_nullable
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de la colonne: {str(e)}")
                    return
                
                # Enregistrer les métadonnées
                new_attr = ModelAttribute(
                    model_name=model_name,
                    attribute_name=attribute_name,
                    attribute_type=attribute_type,
                    max_length=max_length,
                    default_value=default_value,
                    is_nullable=is_nullable,
                    display_name=display_name
                )
                session.add(new_attr)
                message = "Attribut ajouté avec succès!"
            
            session.commit()
            QMessageBox.information(self, "Succès", message)
            self.accept()
        
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
        finally:
            session.close()


class SettingsScreen(QWidget):
    """Page de paramètres pour gérer les attributs des modèles"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_attributes()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title = QLabel("Paramètres - Attributs des Modèles")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e1f29; margin-bottom: 5px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Bouton d'ajout
        self.btn_add = QPushButton("Ajouter un attribut")
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
        """)
        self.btn_add.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(self.btn_add)
        
        main_layout.addLayout(header_layout)
        
        # Onglets pour chaque modèle
        self.tab_widget = QTabWidget()
        
        models = ["Eleve", "Professeur", "Classe", "Note", "TypeExamen"]
        for model_name in models:
            tab = self.create_model_tab(model_name)
            self.tab_widget.addTab(tab, model_name)
        
        main_layout.addWidget(self.tab_widget)
    
    def create_model_tab(self, model_name):
        """Crée un onglet pour un modèle"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tableau des attributs
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Nom", "Type", "Longueur max", "Valeur par défaut", "Nullable", "Actions"
        ])
        
        # Configuration
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        
        table.setColumnWidth(0, 50)
        table.setColumnWidth(2, 100)
        table.setColumnWidth(3, 100)
        table.setColumnWidth(5, 80)
        table.setColumnWidth(6, 150)
        
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Stocker la référence pour pouvoir la mettre à jour
        table.setProperty("model_name", model_name)
        
        layout.addWidget(table)
        
        return tab
    
    def load_attributes(self):
        """Charge les attributs pour tous les modèles"""
        session = SessionLocal()
        try:
            for i in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(i)
                table = tab.findChild(QTableWidget)
                if table:
                    model_name = table.property("model_name")
                    self.load_model_attributes(table, model_name)
        finally:
            session.close()
    
    def load_model_attributes(self, table, model_name):
        """Charge les attributs d'un modèle spécifique (base + personnalisés)"""
        from app.databases.db import engine
        from app.utils.dynamic_tables import get_column_display_name
        
        session = SessionLocal()
        try:
            # Récupérer toutes les colonnes de la table depuis la base de données
            table_name = DynamicSchemaManager.get_table_name(model_name)
            inspector = inspect(engine)
            
            try:
                columns_info = inspector.get_columns(table_name)
            except Exception as e:
                print(f"Erreur lors de la récupération des colonnes: {e}")
                columns_info = []
            
            # Récupérer les attributs personnalisés enregistrés
            custom_attributes = session.query(ModelAttribute).filter(
                ModelAttribute.model_name == model_name
            ).all()
            
            # Créer un dictionnaire des attributs personnalisés par nom
            custom_attrs_dict = {attr.attribute_name: attr for attr in custom_attributes}
            
            # Colonnes de base à exclure (relations, clés étrangères complexes)
            excluded_base_columns = {
                "Eleve": ["classe_actuelle_id"],  # On garde contact_parent
                "Professeur": [],
                "Classe": [],
                "Note": ["eleve_id", "type_examen_id", "classe_id"],
                "TypeExamen": []
            }
            
            excluded = excluded_base_columns.get(model_name, [])
            
            # Préparer la liste de tous les attributs à afficher
            all_attributes = []
            
            # Ajouter les colonnes de base
            for col_info in columns_info:
                col_name = col_info['name']
                
                # Ignorer les colonnes exclues
                if col_name in excluded:
                    continue
                
                # Ignorer les colonnes qui sont déjà dans les attributs personnalisés
                if col_name in custom_attrs_dict:
                    continue
                
                # Créer un objet virtuel pour les attributs de base
                base_attr = type('BaseAttr', (), {
                    'id': None,  # Pas d'ID pour les attributs de base
                    'attribute_name': col_name,
                    'display_name': get_column_display_name(model_name, col_name),
                    'attribute_type': self._infer_type_from_sql_type(col_info['type']),
                    'max_length': col_info.get('length'),
                    'default_value': str(col_info.get('default', '')) if col_info.get('default') else None,
                    'is_nullable': col_info.get('nullable', True),
                    'is_base': True  # Marquer comme attribut de base
                })()
                
                all_attributes.append(base_attr)
            
            # Ajouter les attributs personnalisés
            for attr in custom_attributes:
                attr.is_base = False  # Marquer comme personnalisé
                all_attributes.append(attr)
            
            # Trier par nom
            all_attributes.sort(key=lambda x: x.attribute_name)
            
            # Afficher dans le tableau
            table.setRowCount(len(all_attributes))
            
            for row, attr in enumerate(all_attributes):
                # ID (vide pour les attributs de base)
                if attr.is_base:
                    item_id = QTableWidgetItem("-")
                else:
                    item_id = QTableWidgetItem(str(attr.id))
                item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 0, item_id)
                
                # Nom
                display_name = attr.display_name if hasattr(attr, 'display_name') and attr.display_name else attr.attribute_name
                item_name = QTableWidgetItem(display_name)
                if attr.is_base:
                    item_name.setForeground(QColor("#666666"))  # Gris pour les attributs de base
                table.setItem(row, 1, item_name)
                
                # Type
                type_str = attr.attribute_type
                if hasattr(attr, 'max_length') and attr.max_length:
                    type_str += f"({attr.max_length})"
                item_type = QTableWidgetItem(type_str)
                item_type.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 2, item_type)
                
                # Longueur max
                max_len = attr.max_length if hasattr(attr, 'max_length') else None
                item_max = QTableWidgetItem(str(max_len) if max_len else "")
                item_max.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 3, item_max)
                
                # Valeur par défaut
                default_val = attr.default_value if hasattr(attr, 'default_value') else None
                item_default = QTableWidgetItem(default_val or "")
                table.setItem(row, 4, item_default)
                
                # Nullable
                nullable = attr.is_nullable if hasattr(attr, 'is_nullable') else True
                item_nullable = QTableWidgetItem("Oui" if nullable else "Non")
                item_nullable.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 5, item_nullable)
                
                # Actions (seulement pour les attributs personnalisés)
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                actions_layout.setSpacing(5)
                
                if not attr.is_base:
                    btn_delete = QPushButton("Supprimer")
                    btn_delete.setFixedSize(70, 30)
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
                    """)
                    btn_delete.clicked.connect(lambda checked, aid=attr.id: self.delete_attribute(aid))
                    actions_layout.addWidget(btn_delete)
                else:
                    # Pour les attributs de base, afficher "Système"
                    label_system = QLabel("Système")
                    label_system.setStyleSheet("color: #999; font-style: italic;")
                    actions_layout.addWidget(label_system)
                
                actions_layout.addStretch()
                
                table.setCellWidget(row, 6, actions_widget)
        
        finally:
            session.close()
    
    def _infer_type_from_sql_type(self, sql_type):
        """Infère le type Python depuis le type SQL"""
        type_str = str(sql_type).upper()
        
        if "VARCHAR" in type_str or "TEXT" in type_str or "CHAR" in type_str:
            return "String"
        elif "INTEGER" in type_str:
            return "Integer"
        elif "REAL" in type_str or "FLOAT" in type_str or "DOUBLE" in type_str:
            return "Float"
        elif "DATE" in type_str:
            if "TIME" in type_str:
                return "DateTime"
            return "Date"
        elif "BOOLEAN" in type_str:
            return "Boolean"
        else:
            return "String"  # Par défaut
    
    def show_add_dialog(self):
        """Affiche le dialogue d'ajout"""
        current_tab = self.tab_widget.currentWidget()
        table = current_tab.findChild(QTableWidget)
        model_name = table.property("model_name") if table else None
        
        dialog = AttributeFormDialog(self, model_name=model_name)
        if dialog.exec():
            self.load_attributes()
    
    def delete_attribute(self, attribute_id):
        """Supprime un attribut"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cet attribut ?\n\n"
            "Note: La suppression de la colonne dans la base de données nécessite "
            "de recréer la table. Seules les métadonnées seront supprimées.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = SessionLocal()
            try:
                attr = session.query(ModelAttribute).filter(
                    ModelAttribute.id == attribute_id
                ).first()
                if attr:
                    session.delete(attr)
                    session.commit()
                    QMessageBox.information(self, "Succès", "Attribut supprimé des métadonnées!")
                    self.load_attributes()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
            finally:
                session.close()


