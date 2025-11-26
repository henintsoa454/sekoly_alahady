from sqlalchemy import (
    Column, Integer, String, Float, Date,
    ForeignKey, Table
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ----------- TABLE ASSO PROFESSEUR <-> CLASSE -----------
professeur_classes = Table(
    "professeur_classes",
    Base.metadata,
    Column("professeur_id", Integer, ForeignKey("professeurs.id")),
    Column("classe_id", Integer, ForeignKey("classes.id"))
)

# --------------------- MODELES --------------------------

class Classe(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100), unique=True)

    # Relations inverses
    eleves = relationship("Eleve", back_populates="classe")
    examens = relationship("Examen", back_populates="classe")
    professeurs = relationship("Professeur", secondary=professeur_classes, back_populates="classes")

    def __repr__(self):
        return f"<Classe {self.nom}>"


class Eleve(Base):
    __tablename__ = "eleves"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    classe_id = Column(Integer, ForeignKey("classes.id"))

    classe = relationship("Classe", back_populates="eleves")
    notes = relationship("Note", back_populates="eleve")

    def __repr__(self):
        return f"<Eleve {self.nom} {self.prenom}>"


class Professeur(Base):
    __tablename__ = "professeurs"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    specialite = Column(String(100))

    classes = relationship("Classe", secondary=professeur_classes, back_populates="professeurs")

    def __repr__(self):
        return f"<Professeur {self.nom}>"


class Examen(Base):
    __tablename__ = "examens"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    matiere = Column(String(100))
    date = Column(Date)
    classe_id = Column(Integer, ForeignKey("classes.id"))

    classe = relationship("Classe", back_populates="examens")
    notes = relationship("Note", back_populates="examen")

    def __repr__(self):
        return f"<Examen {self.nom} - {self.matiere}>"


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    eleve_id = Column(Integer, ForeignKey("eleves.id"))
    examen_id = Column(Integer, ForeignKey("examens.id"))
    valeur = Column(Float)

    eleve = relationship("Eleve", back_populates="notes")
    examen = relationship("Examen", back_populates="notes")

    def __repr__(self):
        return f"<Note {self.valeur}>"
