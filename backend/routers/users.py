from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas import UserCreate
from models import User
from db.database import get_db
import models

# 🔐 SÉCURITÉ : Importation de ton module pour générer le token JWT
import security

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    """Test"""
    return db.query(User).all()


@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Créer un compte utilisateur avec vérification de doublon
    """
    # 1. Vérifier si le username existe déjà
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris."
        )

    # 2. Création de l'objet SQLAlchemy (incluant username)
    new_user = User(
        username=user.username,
        name=user.name,
        email=user.email,
        password=user.password
    )

    # Sauvegarde en base
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Utilisateur créé avec succès",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "name": new_user.name,
            "email": new_user.email
        }
    }

@router.get("/by-username/{username}")
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    # On nettoie l'entrée (enlève les espaces)
    search_name = username.strip()
    
    # On cherche l'utilisateur par son username unique
    user = db.query(models.User).filter(models.User.username == search_name).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name
    }

@router.get("/by-email/{email}")
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    search_email = email.strip()
    user = db.query(models.User).filter(models.User.email == search_email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email non reconnu")

    # 🔐 Génération du jeton d'accès pour cet utilisateur
    access_token = security.create_access_token(data={"sub": user.email})

    # Renvoie les informations d'origine complétées par le token JWT intercepté par Kivy
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "access_token": access_token,
        "token_type": "bearer"
    }