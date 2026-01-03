from app.databases.db import SessionLocal
from app.databases.models import Classe, TypeExamen

class DatabaseManager:
    """Gestionnaire de base de données avec initialisation automatique"""
    
    @staticmethod
    def initialize_default_data():
        """Initialise les classes et examens fixes avec ordre hiérarchique"""
        session = SessionLocal()
        try:
            # Classes fixes avec ordre hiérarchique
            classes_fixes = [
                {"nom": "K1A", "ordre": 1, "est_derniere_classe": False},
                {"nom": "K1B", "ordre": 5, "est_derniere_classe": False},
                {"nom": "K2A", "ordre": 2, "est_derniere_classe": False},
                {"nom": "K2B", "ordre": 6, "est_derniere_classe": False},
                {"nom": "K3A", "ordre": 3, "est_derniere_classe": False},
                {"nom": "K3B", "ordre": 7, "est_derniere_classe": False},
                {"nom": "K4A", "ordre": 4, "est_derniere_classe": False},
                {"nom": "K4B", "ordre": 8, "est_derniere_classe": False},
                {"nom": "K5A", "ordre": 9, "est_derniere_classe": False},
                {"nom": "K5B", "ordre": 10, "est_derniere_classe": False},
                {"nom": "K6A", "ordre": 11, "est_derniere_classe": False},
                {"nom": "K6B", "ordre": 12, "est_derniere_classe": False},
                {"nom": "K7A", "ordre": 13, "est_derniere_classe": False},
                {"nom": "K7B", "ordre": 14, "est_derniere_classe": False},
                {"nom": "K8A", "ordre": 15, "est_derniere_classe": False},
                {"nom": "K8B", "ordre": 16, "est_derniere_classe": False},
                {"nom": "K9", "ordre": 17, "est_derniere_classe": False},
                {"nom": "K10", "ordre": 18, "est_derniere_classe": True},
            ]

            type_examen_fixe = [
                {"nom":"Fanadinana Andrana I","abreviation":"FA I"},
                {"nom":"Fanadinana Andrana II","abreviation":"FA II"},
                {"nom":"Fahazotoana","abreviation":"FZ"},
                {"nom":"Fahatongavana","abreviation":"FH"},
                {"nom":"Fanadinana Iombonana","abreviation":"FI"},
                {"nom":"Sala","abreviation":"S"},
            ]
            
            for classe_data in classes_fixes:
                if not session.query(Classe).filter(Classe.nom == classe_data["nom"]).first():
                    session.add(Classe(**classe_data))
            
            for type_examen_data in type_examen_fixe:
                if not session.query(TypeExamen).filter(TypeExamen.nom == type_examen_data["nom"]).first():
                    session.add(TypeExamen(**type_examen_data))
                    
            session.commit()
            print("Classes avec ordre hiérarchique initialisées")
            
        except Exception as e:
            session.rollback()
            print(f"Erreur initialisation données: {e}")
        finally:
            session.close()