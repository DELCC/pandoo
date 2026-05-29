import os  # <-- AJOUTÉ
import json # <-- AJOUTÉ
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

# 🌟 EN PRODUCTION : Il faudra supprimer cette ligne et passer ton serveur en HTTPS !
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # <-- AJOUTÉ

# --- CHARGEMENT DE LA BASE NUTRITIONNELLE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "nutri_data.json")

try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        nutri_db = json.load(f)
    print("✅ Base nutritionnelle Pandoo chargée avec succès !")
except Exception as e:
    print(f"⚠️ Attention : Impossible de charger nutri_data.json : {e}")
    nutri_db = {}

# Importation de la base de données et des modèles
from db.database import engine, get_db 
import models

# Importation des routeurs
from routers import users, children, products, auth 

# 🌟 IMPORTATION DE TON NOUVEAU FICHIER DE SÉCURITÉ
import security

# --- SCHÉMA DE CONNEXION ---
class LoginData(BaseModel):
    email: str
    password: str

# --- CRÉATION DES TABLES ---
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pandoo API",
    description="Backend pour l'application de nutrition enfantine",
    version="1.1.0"
)

# --- MIDDLEWARES ---

# Requis pour l'authentification Google (Authlib)
app.add_middleware(SessionMiddleware, secret_key="pandoo_super_secret_key")

# CONFIGURATION CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTE LOGIN CLASSIQUE SÉCURISÉE ---
@app.post("/login", tags=["Authentication"])
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Email non reconnu")
    
    # 🔐 VÉRIFICATION SÉCURISÉE : Utilise la logique Bcrypt de ton security.py
    if not security.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    
    # 🔐 GÉNÉRATION DU JETON JWT ACCÈS
    access_token = security.create_access_token(data={"sub": user.email})
    
    # On retourne le profil de l'utilisateur ET le badge d'accès (token) pour Kivy
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
        "status": "success"
    }

# --- INCLUSION DES ROUTEURS ---
app.include_router(users.router)
app.include_router(children.router)
app.include_router(products.router)
app.include_router(auth.router)

@app.get("/", tags=["Root"])
async def read_root():
    return JSONResponse(
        content={"message": "API Pandoo opérationnelle"},
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)