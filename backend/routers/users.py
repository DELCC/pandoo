from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas import UserCreate, UserRead, UserLogin, Token
from models import User
from db.database import get_db
from core.security import hash_password, create_access_token, verify_password, get_current_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ✅ Renommé /signup + retourne un token après création
@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà utilisé"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Génération du token directement après création
    access_token = create_access_token(subject=new_user.email)
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/signin", response_model=Token)
def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

