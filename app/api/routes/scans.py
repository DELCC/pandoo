from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.scan import Scan
from app.models.reward import Reward
from app.schemas.scan import ScanCreate, ScanResponse
from uuid import UUID
import httpx
from datetime import datetime

router = APIRouter(prefix="/scans", tags=["Scans"])

ALCOHOL_CATEGORIES = ["alcoholic-beverages", "beers", "wines", "spirits"]

def get_color_rating(nutriscore: str) -> str:
    if nutriscore in ["a", "b"]:
        return "green"
    elif nutriscore in ["c"]:
        return "orange"
    elif nutriscore in ["d", "e"]:
        return "red"
    return "orange"

async def fetch_product(barcode: str) -> dict:
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        data = response.json()
        if data.get("status") != 1:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        return data["product"]

async def check_rewards(child_id: UUID, db: AsyncSession, last_scan_id: UUID):
    result = await db.execute(select(Scan).where(Scan.child_id == child_id))
    scans = result.scalars().all()
    scan_count = len(scans)

    reward_type = None
    if scan_count % 15 == 0:
        reward_type = "game"
    elif scan_count % 10 == 0:
        reward_type = "story"
    elif scan_count % 5 == 0:
        reward_type = "quiz"

    if reward_type:
        new_reward = Reward(
            child_id=child_id,
            scan_id=last_scan_id,
            reward_type=reward_type,
            is_unlocked=True,
            unlocked_at=datetime.utcnow()
        )
        db.add(new_reward)
        await db.commit()

@router.post("/", response_model=ScanResponse)
async def scan_product(scan_data: ScanCreate, db: AsyncSession = Depends(get_db)):
    product = await fetch_product(scan_data.barcode)

    product_name = product.get("product_name", "Produit inconnu")
    nutriscore = product.get("nutriscore_grade", "").lower()
    categories = product.get("categories_tags", [])

    is_alcohol = any(cat in categories for cat in ALCOHOL_CATEGORIES)
    color_rating = get_color_rating(nutriscore)

    new_scan = Scan(
        child_id=scan_data.child_id,
        barcode=scan_data.barcode,
        product_name=product_name,
        nutriscore=nutriscore,
        color_rating=color_rating,
        is_alcohol=is_alcohol
    )
    db.add(new_scan)
    await db.commit()
    await db.refresh(new_scan)

    await check_rewards(scan_data.child_id, db, new_scan.id)

    return new_scan

@router.get("/{child_id}", response_model=list[ScanResponse])
async def get_scans(child_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Scan).where(Scan.child_id == child_id))
    return result.scalars().all()