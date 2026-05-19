from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date 

# --- SCHÉMAS UTILISATEUR ---
class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password : str

class UserRead(BaseModel):
    id: int
    username: str 
    name: str
    email: EmailStr
    
    class Config:
        from_attributes = True

# CÔTÉ BACKEND (Serveur)
class ChildCreate(BaseModel):
    name: str
    birthdate: date
    id_parent: int
    allergies: Optional[str] = "" # <-- AJOUT : Permet de recevoir les allergies au POST

class ChildRead(BaseModel):
    id : int
    name : str
    birthdate : date
    id_parent : int
    allergies: Optional[str] = "" # <-- AJOUT : Permet de renvoyer les allergies au GET
    
    class Config:
        from_attributes = True

# --- SCHÉMAS PRODUIT ---
class ProductCreate(BaseModel):
    barcode: int
    type: str
    name: str
    brand: str
    calories: float
    glucides: float
    calcium: float
    proteins: float
    lipids: float
    salt: float

class ProductRead(BaseModel):
    id : int
    barcode : int
    type : str
    name : str
    brand : str
    calories: float
    glucides: float
    calcium: float
    proteins : float
    lipids : float
    salt : float
    id_child : int
    
    class Config:
        from_attributes = True

# --- SCHÉMAS STORY (Options) ---
class StoryCreate(BaseModel):
    pass

class StoryRead(BaseModel):
    pass