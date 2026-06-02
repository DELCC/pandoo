from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.child import Child
from app.schemas.child import ChildCreate, ChildResponse
from uuid import UUID

router = APIRouter(prefix="/children", tags=["Children"])

@router.post("/", response_model=ChildResponse)
async def create_child(child_data: ChildCreate, user_id: UUID, db: AsyncSession = Depends(get_db)):
    new_child = Child(
        user_id=user_id,
        first_name=child_data.first_name,
        birth_date=child_data.birth_date,
        allergens=child_data.allergens
    )
    db.add(new_child)
    await db.commit()
    await db.refresh(new_child)
    return new_child

@router.get("/{child_id}", response_model=ChildResponse)
async def get_child(child_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Child).where(Child.id == child_id))
    child = result.scalar_one_or_none()
    if not child:
        raise HTTPException(status_code=404, detail="Enfant non trouvé")
    return child