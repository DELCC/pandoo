from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import models
from pydantic import BaseModel
from typing import Optional # AJOUTÉ
from datetime import date 

router = APIRouter(prefix="/children", tags=["Children"])

# --- SCHÉMA DE DONNÉES (Pydantic) ---
class ChildCreate(BaseModel):
    name: str
    birthdate: date  
    id_parent: int
    allergies: Optional[str] = "" # <-- AJOUTÉ

# --- ROUTES ---

@router.post("/")
def create_child(child_data: ChildCreate, db: Session = Depends(get_db)):
    # 1. Vérification de l'existence du parent
    parent = db.query(models.User).filter(models.User.id == child_data.id_parent).first()
    
    if not parent:
        raise HTTPException(status_code=404, detail="Parent non trouvé dans la base de données")

    # 2. Création de l'instance d'enfant avec les allergies
    new_child = models.Child(
        name=child_data.name,
        birthdate=child_data.birthdate,
        id_parent=child_data.id_parent,
        allergies=child_data.allergies # <-- AJOUTÉ
    )
    
    db.add(new_child)
    db.commit()
    db.refresh(new_child)
    
    return {
        "status": "success",
        "message": f"Enfant {new_child.name} créé avec succès",
        "child": {
            "id": new_child.id,
            "name": new_child.name,
            "birthdate": new_child.birthdate,
            "id_parent": new_child.id_parent,
            "allergies": new_child.allergies # <-- AJOUTÉ
        }
    }

@router.get("/parent/{parent_id}")
def get_children_by_parent(parent_id: int, db: Session = Depends(get_db)):
    """Récupère la liste de tous les enfants pour un parent donné"""
    children = db.query(models.Child).filter(models.Child.id_parent == parent_id).all()
    return children

@router.get("/{child_id}")
def get_child_details(child_id: int, db: Session = Depends(get_db)):
    """Récupère les détails d'un enfant spécifique"""
    child = db.query(models.Child).filter(models.Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Enfant non trouvé")
    return child