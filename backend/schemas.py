from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password : str

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr


class ChildCreate(BaseModel):
    name : str
    birthdate : str
    id_parent : int
    allergenes : str

class ChildRead(BaseModel):
    id : int
    name : str
    birthdate : str
    id_parent : int
    allergenes : str

class ProductCreate(BaseModel):
    barcode : str
    type : str
    name : str
    brand : str
    calories: float
    calcium: float
    proteins : float
    lipids : float
    salt : float


class ProductRead(BaseModel):
    id : int
    barcode : int
    type : str
    name : str
    brand : str
    calories: float
    calcium: float
    proteins : float
    lipids : float
    salt : float
    id_child : int

class UserLogin(BaseModel):
    email: str
    password: str

class StoryCreate(BaseModel):
    pass

class StoryRead(BaseModel):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

# Les données contenues à l'intérieur du token (utilisé pour la validation interne)
class TokenData(BaseModel):
    email: Optional[str] = None

class FirebaseTokenRequest(BaseModel):
    id_token: str

class ProductScan(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    calories: Optional[float] = None
    calcium: Optional[float] = None
    proteins: Optional[float] = None
    lipids: Optional[float] = None
    salt: Optional[float] = None

model_config = {"from_attributes": True} # Permet de lire un objet ORM SqlAlchemy