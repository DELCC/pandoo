from fastapi import FastAPI
from app.db.database import engine
from app.db.base import Base
from app.models import User, Child, Scan, Reward
from app.api.routes.auth import router as auth_router
from app.api.routes.children import router as children_router
from app.api.routes.scans import router as scans_router
from app.api.routes.rewards import router as rewards_router

app = FastAPI(
    title="Pandoo API",
    description="Le backend de Pandoo, l'application nutrition pour enfants 🐼",
    version="0.1.0"
)

app.include_router(auth_router)
app.include_router(children_router)
app.include_router(scans_router)
app.include_router(rewards_router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Pandoo 🐼"}