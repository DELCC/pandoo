from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.reward import Reward
from app.models.scan import Scan
from app.models.child import Child
from app.schemas.reward import RewardResponse
from app.services.ai_service import generate_story, generate_quiz
from uuid import UUID
from datetime import date

router = APIRouter(prefix="/rewards", tags=["Rewards"])

def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )

@router.get("/{child_id}", response_model=list[RewardResponse])
async def get_rewards(child_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reward).where(Reward.child_id == child_id))
    return result.scalars().all()

@router.post("/{reward_id}/generate", response_model=RewardResponse)
async def generate_reward_content(reward_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reward).where(Reward.id == reward_id))
    reward = result.scalar_one_or_none()
    if not reward:
        raise HTTPException(status_code=404, detail="Récompense non trouvée")

    child_result = await db.execute(select(Child).where(Child.id == reward.child_id))
    child = child_result.scalar_one_or_none()

    scan_result = await db.execute(select(Scan).where(Scan.id == reward.scan_id))
    scan = scan_result.scalar_one_or_none()

    product_name = scan.product_name if scan else "un produit mystère"
    child_age = calculate_age(child.birth_date)

    if reward.reward_type == "story":
        product_category = scan.product_name if scan else "aventure"
        content = await generate_story(child.first_name, product_name, child_age, product_category)
    elif reward.reward_type == "quiz":
        content = await generate_quiz(product_name, child_age)
    else:
        content = "Un jeu arrive bientôt !"

    reward.content = content
    await db.commit()
    await db.refresh(reward)
    return reward