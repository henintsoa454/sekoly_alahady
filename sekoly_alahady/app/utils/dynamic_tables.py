"""Utilitaires pour créer des tableaux dynamiques basés sur les modèles"""
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from app.databases.db import SessionLocal
from app.databases.models import ModelAttribute
from app.databases.dynamic_schema import DynamicSchemaManager


def get_dynamic_columns(model_name, include_base=True):
    """Récupère toutes les colonnes d'un modèle (base + personnalisées)"""
    # Colonnes de base pour chaque modèle
    base_columns = {
        "Eleve": ["id", "nom", "prenom", "date_naissance", "sexe", "classe_actuelle_id", "contact_parent"],
        "Professeur": ["id", "nom", "prenom", "date_naissance", "sexe"],
        "Classe": ["id", "nom", "ordre", "est_derniere_classe"],
        "Note": ["id", "eleve_id", "type_examen_id", "classe_id", "note", "date_insertion", "date_examen"],
        "TypeExamen": ["id", "nom", "abreviation"]
    }
    
    columns = []
    if include_base:
        columns = base_columns.get(model_name, []).copy()
    
    # Ajouter les colonnes personnalisées depuis la base de données
    session = SessionLocal()
    try:
        # Récupérer les colonnes réelles de la table
        actual_columns = DynamicSchemaManager.get_model_columns(model_name)
        
        # Ajouter les colonnes qui existent dans la table mais pas dans la liste de base
        for col in actual_columns:
            if col not in columns:
                # Vérifier si c'est un attribut personnalisé enregistré
                attr = session.query(ModelAttribute).filter(
                    ModelAttribute.model_name == model_name,
                    ModelAttribute.attribute_name == col
                ).first()
                
                if attr or col not in base_columns.get(model_name, []):
                    columns.append(col)
    finally:
        session.close()
    
    return columns


def get_column_display_name(model_name, column_name):
    """Récupère le nom d'affichage d'une colonne"""
    # Noms d'affichage par défaut
    default_names = {
        "Eleve": {
            "id": "ID",
            "nom": "Nom",
            "prenom": "Prénom",
            "date_naissance": "Date Naissance",
            "sexe": "Sexe",
            "classe_actuelle_id": "Classe",
            "contact_parent": "Contact Parent"
        },
        "Professeur": {
            "id": "ID",
            "nom": "Nom",
            "prenom": "Prénom",
            "date_naissance": "Date Naissance",
            "sexe": "Sexe"
        },
        "Classe": {
            "id": "ID",
            "nom": "Nom",
            "ordre": "Ordre",
            "est_derniere_classe": "Dernière classe"
        },
        "Note": {
            "id": "ID",
            "eleve_id": "Élève",
            "type_examen_id": "Type Examen",
            "classe_id": "Classe",
            "note": "Note",
            "date_insertion": "Date Insertion",
            "date_examen": "Date Examen"
        },
        "TypeExamen": {
            "id": "ID",
            "nom": "Nom",
            "abreviation": "Abréviation"
        }
    }
    
    # Vérifier dans les métadonnées
    session = SessionLocal()
    try:
        attr = session.query(ModelAttribute).filter(
            ModelAttribute.model_name == model_name,
            ModelAttribute.attribute_name == column_name
        ).first()
        
        if attr and attr.display_name:
            return attr.display_name
    finally:
        session.close()
    
    # Retourner le nom par défaut ou le nom de la colonne
    return default_names.get(model_name, {}).get(column_name, column_name.replace("_", " ").title())


def setup_dynamic_table(table, model_name, columns_to_show=None, exclude_columns=None):
    """Configure un tableau avec les colonnes dynamiques"""
    if columns_to_show is None:
        columns_to_show = get_dynamic_columns(model_name)
    
    if exclude_columns:
        columns_to_show = [col for col in columns_to_show if col not in exclude_columns]
    
    # Configurer les colonnes
    table.setColumnCount(len(columns_to_show))
    
    headers = [get_column_display_name(model_name, col) for col in columns_to_show]
    table.setHorizontalHeaderLabels(headers)
    
    # Configuration par défaut
    header = table.horizontalHeader()
    for i in range(len(columns_to_show)):
        if columns_to_show[i] == "id":
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(i, 50)
        elif columns_to_show[i] in ["nom", "prenom"]:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        else:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(i, 120)
    
    return columns_to_show


def get_value_from_model(instance, column_name, model_name):
    """Récupère la valeur d'une colonne depuis une instance de modèle"""
    # Colonnes de relation (à gérer séparément)
    relation_columns = {
        "Eleve": ["classe_actuelle_id"],
        "Professeur": [],
        "Classe": [],
        "Note": ["eleve_id", "type_examen_id", "classe_id"],
        "TypeExamen": []
    }
    
    # Si c'est une colonne de relation, retourner l'ID ou le nom
    if column_name in relation_columns.get(model_name, []):
        if hasattr(instance, column_name):
            value = getattr(instance, column_name)
            # Essayer de récupérer l'objet lié
            if column_name == "classe_actuelle_id" and hasattr(instance, "classe_actuelle"):
                if instance.classe_actuelle:
                    return instance.classe_actuelle.nom
            return str(value) if value else ""
    
    # Colonnes normales
    if hasattr(instance, column_name):
        value = getattr(instance, column_name)
        
        # Formater selon le type
        if value is None:
            return ""
        
        # Dates
        if hasattr(value, 'strftime'):
            return value.strftime("%d/%m/%Y")
        
        # Booléens
        if isinstance(value, bool):
            return "Oui" if value else "Non"
        
        # Enums
        if hasattr(value, 'value'):
            return str(value.value)
        
        return str(value)
    
    return ""

