from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas import ChildCreate, ChildRead
from models import Child, User
from db.database import get_db
# Import de la dépendance de sécurité
from core.security import get_current_user 

router = APIRouter(
    prefix="/children",
    tags=["Children"]
)

@router.post("/", response_model=ChildRead) # Plus de {parent_id} ici
def create_child(
    child: ChildCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Le parent est l'user connecté
):
    """
    Créer un enfant lié au parent connecté (via le token)
    """
    new_child = Child(
        name=child.name,
        birthdate=child.birthdate,
        allergenes=child.allergenes,
        id_parent=current_user.id # Utilisation directe de l'ID du token
    )

    db.add(new_child)
    db.commit()
    db.refresh(new_child)
    return new_child


@router.get("/", response_model=list[ChildRead])
def list_my_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Liste uniquement les enfants appartenant à l'utilisateur connecté
    """
    return db.query(Child).filter(Child.id_parent == current_user.id).all()


@router.put("/{child_id}", response_model=ChildRead)
def update_child(
    child_id: int, 
    child_update: ChildCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Met à jour un enfant, seulement s'il appartient à l'utilisateur connecté
    """
    child = db.query(Child).filter(
        Child.id == child_id, 
        Child.id_parent == current_user.id
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Enfant non trouvé")

    child.name = child_update.name
    child.age = child_update.age
    
    db.commit()
    db.refresh(child)
    return child


@router.delete("/{child_id}")
def delete_child(
    child_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime un enfant, seulement s'il appartient à l'utilisateur connecté
    """
    child = db.query(Child).filter(
        Child.id == child_id, 
        Child.id_parent == current_user.id
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Enfant non trouvé")

    db.delete(child)
    db.commit()
    return {"message": "Enfant supprimé avec succès"}