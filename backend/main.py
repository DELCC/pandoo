from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from db.database import get_db
from routers import users, children, products, stories
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

# --- Configuration du CORS pour Expo ---
# Le wildcard "*" est essentiel pour le développement mobile (Android/iOS/Expo Go)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines (indispensable pour le mobile)
    allow_credentials=True,
    allow_methods=["*"],  # Autorise GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Autorise Authorization, Content-Type, etc.
)

app.include_router(users.router)
app.include_router(children.router)
app.include_router(products.router)
app.include_router(stories.router)

@app.get("/")
def root():
    return {"message": "API OK"}


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "Connexion DB OK"}

    except Exception as e:
        return {"error": str(e)}


