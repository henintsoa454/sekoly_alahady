from sqlalchemy import (
    Column, Integer, String, Float, Date,
    ForeignKey, Table, Boolean, Enum, DateTime
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

# Enum pour le sexe
class SexeEnum(enum.Enum):
    MASCULIN = "M"
    FEMININ = "F"

# ----------- TABLE HISTORIQUE ELEVE <-> CLASSE -----------
eleve_classe_historique = Table(
    "eleve_classe_historique",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("eleve_id", Integer, ForeignKey("eleves.id")),
    Column("classe_id", Integer, ForeignKey("classes.id")),
    Column("date_debut", DateTime, server_default=func.now()),  # Date d'entrée dans la classe
    Column("date_fin", DateTime, nullable=True)  # Date de sortie de la classe (si null, c'est la classe actuelle)
)

# ----------- TABLE HISTORIQUE PROFESSEUR <-> CLASSE -----------
professeur_classe_historique = Table(
    "professeur_classe_historique",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("professeur_id", Integer, ForeignKey("professeurs.id")),
    Column("classe_id", Integer, ForeignKey("classes.id")),
    Column("date_modification", DateTime, server_default=func.now())
)

# --------------------- MODELES --------------------------

class Classe(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100), unique=True)
    ordre = Column(Integer, unique=True, nullable=False)
    est_derniere_classe = Column(Boolean, default=False)

    # Relations inverses
    eleves_actuels = relationship("Eleve", back_populates="classe_actuelle")
    professeurs_actuels = relationship("Professeur", secondary="professeur_classes", 
                                       back_populates="classes_actuelles")
    
    # Historique
    historique_eleves = relationship("Eleve", secondary=eleve_classe_historique, 
                                    back_populates="historique_classes")
    historique_professeurs = relationship("Professeur", secondary=professeur_classe_historique, 
                                         back_populates="historique_classes")
    
    # Notes associées à cette classe
    notes = relationship("Note", back_populates="classe")

    def __repr__(self):
        return f"<Classe {self.nom}>"


class Eleve(Base):
    __tablename__ = "eleves"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    date_naissance = Column(Date, nullable=False)
    sexe = Column(Enum(SexeEnum), nullable=False)
    classe_actuelle_id = Column(Integer, ForeignKey("classes.id"))  # Classe actuelle
    contact_parent = Column(String(20))

    # Classe actuelle
    classe_actuelle = relationship("Classe", back_populates="eleves_actuels")
    
    # Historique des classes
    historique_classes = relationship("Classe", secondary=eleve_classe_historique, 
                                     back_populates="historique_eleves")
    
    # Notes
    notes = relationship("Note", back_populates="eleve")

    def __repr__(self):
        return f"<Eleve {self.nom} {self.prenom}>"


class Professeur(Base):
    __tablename__ = "professeurs"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    date_naissance = Column(Date, nullable=False)
    sexe = Column(Enum(SexeEnum), nullable=False)

    # Classes actuelles
    classes_actuelles = relationship("Classe", secondary="professeur_classes", 
                                    back_populates="professeurs_actuels")
    
    # Historique des classes
    historique_classes = relationship("Classe", secondary=professeur_classe_historique, 
                                     back_populates="historique_professeurs")

    def __repr__(self):
        return f"<Professeur {self.nom} {self.prenom}>"


class TypeExamen(Base):
    __tablename__ = "type_examens"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100), unique=True)  # Nom complet de l'examen
    abreviation = Column(String(20), unique=True)  # Abréviation

    # Relation avec les notes
    notes = relationship("Note", back_populates="type_examen")

    def __repr__(self):
        return f"<TypeExamen {self.nom} ({self.abreviation})>"


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    eleve_id = Column(Integer, ForeignKey("eleves.id"))
    type_examen_id = Column(Integer, ForeignKey("type_examens.id"))  # Référence au type d'examen
    
    # AJOUT IMPORTANT: Référence à la classe au moment où la note a été attribuée
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)  # La classe de l'élève au moment de l'examen
    
    note = Column(Float)  # Note sur 20
    date_insertion = Column(DateTime, server_default=func.now())
    date_examen = Column(Date, nullable=False)  # Date à laquelle l'examen a eu lieu

    eleve = relationship("Eleve", back_populates="notes")
    type_examen = relationship("TypeExamen", back_populates="notes")
    
    # AJOUT IMPORTANT: Relation avec la classe
    classe = relationship("Classe", back_populates="notes")

    def __repr__(self):
        return f"<Note {self.note} - {self.type_examen.nom if self.type_examen else ''}>"


# Table d'association pour les classes actuelles des professeurs
professeur_classes = Table(
    "professeur_classes",
    Base.metadata,
    Column("professeur_id", Integer, ForeignKey("professeurs.id")),
    Column("classe_id", Integer, ForeignKey("classes.id"))
)


# Modèle pour les attributs personnalisés des modèles
class ModelAttribute(Base):
    __tablename__ = "model_attributes"
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(50), nullable=False)  # Nom du modèle (Eleve, Professeur, etc.)
    attribute_name = Column(String(100), nullable=False)  # Nom de l'attribut/colonne
    attribute_type = Column(String(50), nullable=False)  # Type: String, Integer, Float, Date, Boolean
    default_value = Column(String(200), nullable=True)  # Valeur par défaut (stockée en string)
    max_length = Column(Integer, nullable=True)  # Pour String
    is_nullable = Column(Boolean, default=True)  # Si la colonne peut être NULL
    display_name = Column(String(100), nullable=True)  # Nom d'affichage dans l'interface
    
    def __repr__(self):
        return f"<ModelAttribute {self.model_name}.{self.attribute_name}>"