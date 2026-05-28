from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas import StoryRead, StoryCreate
from models import Child, Story, User
from db.database import get_db
from core.security import get_current_user



router = APIRouter(prefix='/stories', tags=["Stories"])



@router.post("/{id_child}", response_model=StoryRead)
def add_story(
    id_child: int,
    story_in: StoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée une histoire pour un enfant spécifique,
    seulement si cet enfant appartient à l'utilisateur connecté.
    """
    child = db.query(Child).filter(
        Child.id == id_child,
        Child.id_parent == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=404,
            detail="Enfant non trouvé ou accès non autorisé"
        )

    new_story = Story(
        url_mp3=story_in.url_mp3,
        script=story_in.script,
        id_child=child.id
    )

    db.add(new_story)
    db.commit()
    db.refresh(new_story)

    return new_story


@router.get("/{id_child}", response_model=list[StoryRead])
def get_stories(
    id_child: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère toutes les histoires d'un enfant,
    seulement si l'utilisateur connecté est son parent.
    """
    child = db.query(Child).filter(
        Child.id == id_child,
        Child.id_parent == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=404,
            detail="Accès refusé ou enfant introuvable"
        )

    return db.query(Story).filter(Story.id_child == id_child).all()



