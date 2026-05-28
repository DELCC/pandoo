from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from db.database import get_db
from models import User

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret")
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/signin")

def normalize_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def hash_password(password: str):
    return pwd_context.hash(normalize_password(password))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(
        normalize_password(plain_password),
        hashed_password
    )

def create_access_token(subject: str, expires_delta: int = 60) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)

    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "access"
    }

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dépendance pour récupérer l'utilisateur actuellement connecté
    via son JWT Token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Décoder le token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Extraire l'identifiant (souvent stocké dans le champ 'sub')
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        # Si le token est expiré ou malformé
        raise credentials_exception

    # 3. Chercher l'utilisateur dans la base de données
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise credentials_exception
        
    # 4. Retourner l'objet utilisateur
    return user