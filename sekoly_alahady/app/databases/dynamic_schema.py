"""Module pour gérer dynamiquement les schémas de base de données"""
from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError
from app.databases.db import engine, SessionLocal
from app.databases.models import ModelAttribute


class DynamicSchemaManager:
    """Gestionnaire pour les modifications dynamiques du schéma"""
    
    TYPE_MAPPING = {
        "String": "TEXT",
        "Integer": "INTEGER",
        "Float": "REAL",
        "Date": "DATE",
        "DateTime": "DATETIME",
        "Boolean": "INTEGER"  # SQLite utilise INTEGER pour BOOLEAN
    }
    
    @staticmethod
    def get_table_name(model_name):
        """Convertit le nom du modèle en nom de table"""
        model_to_table = {
            "Eleve": "eleves",
            "Professeur": "professeurs",
            "Classe": "classes",
            "Note": "notes",
            "TypeExamen": "type_examens"
        }
        return model_to_table.get(model_name, model_name.lower() + "s")
    
    @staticmethod
    def column_exists(table_name, column_name):
        """Vérifie si une colonne existe dans une table"""
        session = SessionLocal()
        try:
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            return column_name in columns
        except Exception as e:
            print(f"Erreur lors de la vérification de la colonne: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def add_column(model_name, attribute_name, attribute_type, default_value=None, max_length=None, is_nullable=True):
        """Ajoute une colonne à une table"""
        table_name = DynamicSchemaManager.get_table_name(model_name)
        
        if DynamicSchemaManager.column_exists(table_name, attribute_name):
            raise ValueError(f"La colonne {attribute_name} existe déjà dans la table {table_name}")
        
        sql_type = DynamicSchemaManager.TYPE_MAPPING.get(attribute_type, "TEXT")
        
        if attribute_type == "String" and max_length:
            sql_type = f"VARCHAR({max_length})"
        
        nullable_clause = "" if is_nullable else "NOT NULL"
        default_clause = ""
        
        if default_value is not None:
            if attribute_type == "String":
                default_clause = f"DEFAULT '{default_value}'"
            elif attribute_type == "Integer":
                default_clause = f"DEFAULT {default_value}"
            elif attribute_type == "Float":
                default_clause = f"DEFAULT {default_value}"
            elif attribute_type == "Boolean":
                default_clause = f"DEFAULT {1 if default_value else 0}"
        
        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {attribute_name} {sql_type} {nullable_clause} {default_clause}"
        
        session = SessionLocal()
        try:
            session.execute(text(alter_sql))
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise Exception(f"Erreur lors de l'ajout de la colonne: {str(e)}")
        finally:
            session.close()
    
    @staticmethod
    def drop_column(model_name, attribute_name):
        """Supprime une colonne d'une table (SQLite ne supporte pas DROP COLUMN directement)"""
        # SQLite ne supporte pas DROP COLUMN, il faut recréer la table
        # Pour simplifier, on va juste marquer la colonne comme supprimée dans les métadonnées
        # et l'ignorer dans les requêtes
        table_name = DynamicSchemaManager.get_table_name(model_name)
        
        if not DynamicSchemaManager.column_exists(table_name, attribute_name):
            raise ValueError(f"La colonne {attribute_name} n'existe pas dans la table {table_name}")
        
        # Note: SQLite ne supporte pas DROP COLUMN directement
        # On va utiliser une approche de recréation de table si nécessaire
        # Pour l'instant, on va juste supprimer la métadonnée
        # Une vraie suppression nécessiterait de recréer la table
        raise NotImplementedError(
            "La suppression de colonne nécessite de recréer la table. "
            "Cette fonctionnalité sera implémentée dans une version future."
        )
    
    @staticmethod
    def modify_column(model_name, attribute_name, new_type=None, new_default=None, new_max_length=None, new_nullable=None):
        """Modifie une colonne existante"""
        # SQLite a des limitations pour ALTER COLUMN
        # On va utiliser une approche de recréation si nécessaire
        raise NotImplementedError(
            "La modification de colonne nécessite de recréer la table. "
            "Cette fonctionnalité sera implémentée dans une version future."
        )
    
    @staticmethod
    def get_model_columns(model_name):
        """Récupère toutes les colonnes d'un modèle (y compris les personnalisées)"""
        table_name = DynamicSchemaManager.get_table_name(model_name)
        session = SessionLocal()
        try:
            inspector = inspect(engine)
            columns = inspector.get_columns(table_name)
            return [col['name'] for col in columns]
        except Exception as e:
            print(f"Erreur lors de la récupération des colonnes: {e}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def get_custom_attributes(model_name):
        """Récupère les attributs personnalisés d'un modèle"""
        session = SessionLocal()
        try:
            attributes = session.query(ModelAttribute).filter(
                ModelAttribute.model_name == model_name
            ).all()
            return attributes
        finally:
            session.close()


